/**
 * dfg_to_hgr.cpp  –  LLVM function pass that extracts a dataflow hypergraph
 * and writes it as a .hgr file for the Mocarabe CGRA toolchain.
 *
 * Pass name: dfg-to-hgr
 *
 * Invoke:
 *   opt-18 -load-pass-plugin=./dfg_to_hgr.so \
 *          -passes="mem2reg,dfg-to-hgr"       \
 *          -dfg-out-dir=hgr                    \
 *          input.ll -o /dev/null
 *
 * Node labelling (mirrors mocarabe/cad/netlist.py conventions):
 *   "+"  / "*"           arithmetic operator  (drives one PE type)
 *   identifier string    IO node (input param, output sink, constant)
 *   numeric string       constant IO node
 *
 * Build:
 *   make -C llvm_pass
 */

#include <filesystem>
#include <fstream>
#include <map>
#include <set>
#include <string>
#include <vector>

#include "llvm/IR/Constants.h"
#include "llvm/IR/DebugInfoMetadata.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/IntrinsicInst.h"
#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;
namespace fs = std::filesystem;

// ---------------------------------------------------------------------------
// Command-line option: output directory (default: "hgr")
// ---------------------------------------------------------------------------
static cl::opt<std::string> OutputDir(
    "dfg-out-dir",
    cl::desc("Base directory for .hgr output (default: hgr)"),
    cl::init("hgr"));

// ---------------------------------------------------------------------------
// HGR graph representation
// ---------------------------------------------------------------------------
struct HGR {
    // node id → label
    std::vector<std::string> labels;

    // driver node id → list of sink node ids (one entry per hyperedge/net)
    std::map<int, std::vector<int>> nets;

    int add_node(std::string label) {
        int id = (int)labels.size();
        labels.push_back(std::move(label));
        return id;
    }

    void add_edge(int driver, int sink) {
        nets[driver].push_back(sink);
    }

    void write(const std::string &path) const {
        // count non-empty nets
        int num_nets = 0;
        for (auto &[d, sinks] : nets)
            if (!sinks.empty()) ++num_nets;

        fs::create_directories(fs::path(path).parent_path());
        std::ofstream out(path);
        out << num_nets << " " << labels.size() << "\n";
        for (int i = 0; i < (int)labels.size(); ++i)
            out << i << ":" << labels[i] << "\n";
        out << "--\n";
        for (auto &[driver, sinks] : nets) {
            if (sinks.empty()) continue;
            out << driver;
            for (int s : sinks) out << " " << s;
            out << "\n";
        }
    }
};

// ---------------------------------------------------------------------------
// The pass
// ---------------------------------------------------------------------------
struct DFGPass : PassInfoMixin<DFGPass> {

    PreservedAnalyses run(Function &F, FunctionAnalysisManager &) {
        if (F.isDeclaration()) return PreservedAnalyses::all();

        HGR hgr;

        // Map from LLVM Value* to HGR node id
        std::map<Value *, int> val_to_node;

        // Cache for integer constants: value → node id
        std::map<int64_t, int> const_cache;

        // ── Step 1: collect debug-variable names for all values ──────────
        // dbg.value(Value*, DILocalVariable*, ...) associates an SSA value
        // with a source-level variable name.  We keep the LAST association
        // for each Value* so that reassigned params (e.g. y0 = a0*x0 in
        // iir8) record the destination variable, not the original parameter.
        std::map<Value *, std::string> debug_name;

        for (auto &BB : F)
            for (auto &I : BB)
                if (auto *DV = dyn_cast<DbgValueInst>(&I))
                    if (Value *V = DV->getValue())
                        if (auto *Var = DV->getVariable())
                            debug_name[V] = Var->getName().str();

        // ── Step 2: create input nodes for i32 function arguments ────────
        // Skip arguments with no uses: after mem2reg, by-value params that
        // are immediately overwritten (e.g. iir8's y0..y7) have no users.
        for (Argument &A : F.args()) {
            if (!A.getType()->isIntegerTy(32)) continue;
            if (A.use_empty()) continue;

            // Prefer the source-level name from debug info; fall back to
            // "arg<N>" if the IR was compiled without -g.
            std::string name = "arg" + std::to_string(A.getArgNo());
            auto it = debug_name.find(&A);
            if (it != debug_name.end()) name = it->second;

            val_to_node[&A] = hgr.add_node(name);
        }

        // ── Helper: get (or create) a constant node ──────────────────────
        auto get_const_node = [&](int64_t v) -> int {
            auto it = const_cache.find(v);
            if (it != const_cache.end()) return it->second;
            int id = hgr.add_node(std::to_string(v));
            const_cache[v] = id;
            return id;
        };

        // ── Helper: resolve any LLVM value to an HGR node id ────────────
        // Returns -1 if the value is not representable (e.g. undef).
        auto resolve = [&](Value *V) -> int {
            if (auto *CI = dyn_cast<ConstantInt>(V))
                return get_const_node(CI->getSExtValue());
            auto it = val_to_node.find(V);
            return (it != val_to_node.end()) ? it->second : -1;
        };

        // ── Step 3: process instructions ─────────────────────────────────
        for (auto &BB : F) {
            for (auto &I : BB) {
                // Skip debug intrinsics
                if (isa<DbgInfoIntrinsic>(I)) continue;

                // ── arithmetic: add / sub / mul ──────────────────────────
                if (auto *BO = dyn_cast<BinaryOperator>(&I)) {
                    auto opc = BO->getOpcode();
                    if (opc != Instruction::Add &&
                        opc != Instruction::Sub &&
                        opc != Instruction::Mul)
                        continue;  // ignore div, shifts, etc.

                    std::string op_label =
                        (opc == Instruction::Mul) ? "*" : "+";
                    int op_id = hgr.add_node(op_label);
                    val_to_node[BO] = op_id;

                    for (int i = 0; i < 2; ++i) {
                        int src = resolve(BO->getOperand(i));
                        if (src >= 0) hgr.add_edge(src, op_id);
                    }
                    continue;
                }

                // ── store: detect external outputs ───────────────────────
                if (auto *SI = dyn_cast<StoreInst>(&I)) {
                    Value *val_op = SI->getValueOperand();
                    Value *ptr_op = SI->getPointerOperand();

                    // Case A: store i32 %val, ptr %arg  (ptr function arg)
                    // After mem2reg the ptr alloca is eliminated and the
                    // argument pointer appears directly.
                    if (auto *Arg = dyn_cast<Argument>(ptr_op)) {
                        if (Arg->getType()->isPointerTy()) {
                            std::string name =
                                "out" + std::to_string(Arg->getArgNo());
                            auto it = debug_name.find(Arg);
                            if (it != debug_name.end()) name = it->second;

                            int out_id = hgr.add_node(name);
                            int src = resolve(val_op);
                            if (src >= 0) hgr.add_edge(src, out_id);
                        }
                    }
                    continue;
                }
            }
        }

        // ── Step 4: add output sinks for terminal arithmetic values ──────
        // A terminal value is a BinaryOperator whose result is NOT used as
        // an operand by any other BinaryOperator (it's a DFG "leaf").
        // This covers by-value output params (e.g. iir8: y7 = sub ...).
        for (auto &BB : F) {
            for (auto &I : BB) {
                if (isa<DbgInfoIntrinsic>(I)) continue;
                auto *BO = dyn_cast<BinaryOperator>(&I);
                if (!BO) continue;
                auto opc = BO->getOpcode();
                if (opc != Instruction::Add &&
                    opc != Instruction::Sub &&
                    opc != Instruction::Mul)
                    continue;

                // Check: does any user of this value do arithmetic?
                bool has_arith_user = false;
                for (User *U : BO->users()) {
                    if (auto *UBO = dyn_cast<BinaryOperator>(U)) {
                        auto uo = UBO->getOpcode();
                        if (uo == Instruction::Add ||
                            uo == Instruction::Sub ||
                            uo == Instruction::Mul) {
                            has_arith_user = true;
                            break;
                        }
                    }
                }
                if (has_arith_user) continue;

                // Check: is it already connected to an output via a store?
                bool has_store_user = false;
                for (User *U : BO->users())
                    if (isa<StoreInst>(U)) { has_store_user = true; break; }
                if (has_store_user) continue;

                // Terminal arithmetic node: add a named sink
                std::string name;
                auto it = debug_name.find(BO);
                if (it != debug_name.end())
                    name = it->second;
                else
                    name = "out" + std::to_string(val_to_node.size());

                int out_id = hgr.add_node(name);
                int src = val_to_node.count(BO) ? val_to_node[BO] : -1;
                if (src >= 0) hgr.add_edge(src, out_id);
            }
        }

        // ── Step 5: write .hgr ───────────────────────────────────────────
        std::string fname = F.getName().str();
        std::string path =
            OutputDir + "/" + fname + "/" + fname + ".hgr";

        errs() << "[dfg-to-hgr] " << fname
               << "  nodes=" << hgr.labels.size()
               << "  →  " << path << "\n";

        hgr.write(path);
        return PreservedAnalyses::all();
    }

    static bool isRequired() { return true; }
};

// ---------------------------------------------------------------------------
// Plugin registration (new pass manager)
// ---------------------------------------------------------------------------
extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION, "DFGPass", LLVM_VERSION_STRING,
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                   ArrayRef<PassBuilder::PipelineElement>) -> bool {
                    if (Name == "dfg-to-hgr") {
                        FPM.addPass(DFGPass());
                        return true;
                    }
                    return false;
                });
        }};
}
