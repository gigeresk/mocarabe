#!/usr/bin/env bash
# llvm-with-clang.sh  –  LLVM-based DFG extractor for Mocarabe
#
# Analogue of gcc-with-python.sh but uses clang + the dfg-to-hgr LLVM pass.
#
# Usage:
#   ./llvm-with-clang.sh <source.c> <output_base_dir>
#
# Examples:
#   ./llvm-with-clang.sh bench/bitgpu/int_adder_chain.c hgr/
#   ./llvm-with-clang.sh bench/bitgpu/int_poly_quadratic.c hgr/
#   for f in bench/bitgpu/*.c; do ./llvm-with-clang.sh "$f" hgr/; done

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <source.c> <output_base_dir>" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN="${SCRIPT_DIR}/llvm_pass/dfg_to_hgr.so"
OUT_DIR="$2"

if [[ ! -f "$PLUGIN" ]]; then
    echo "Plugin not found: $PLUGIN" >&2
    echo "Run:  make -C ${SCRIPT_DIR}/llvm_pass" >&2
    exit 1
fi

SRC="$1"
STEM="$(basename "$SRC" .c)"
TMP="$(mktemp /tmp/${STEM}_XXXXXX.ll)"
trap 'rm -f "$TMP"' EXIT

# 1. Compile to LLVM IR (-g for debug variable names, -O0 to keep structure)
clang -O0 -Xclang -disable-O0-optnone -g -emit-llvm -S -o "$TMP" "$SRC" 2>/dev/null || \
clang -O0 -g -emit-llvm -S -o "$TMP" "$SRC"

# 2. Run mem2reg then the DFG pass
opt-18 -load-pass-plugin="$PLUGIN" \
       -passes="mem2reg,dfg-to-hgr" \
       -dfg-out-dir="$OUT_DIR" \
       "$TMP" -o /dev/null
