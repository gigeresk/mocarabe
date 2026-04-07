"""
Tests for the LLVM-based DFG extractor (llvm-with-clang.sh + dfg_to_hgr pass).

Checks that the generated .hgr files are structurally valid and can be loaded
by mocarabe's Netlist class.  Does not rebuild the plugin.
"""

import os
import subprocess
import tempfile

import pytest

from mocarabe.cad.netlist import Netlist

MOCARABE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH_DIR = os.path.join(MOCARABE_ROOT, "bench", "bitgpu")
SCRIPT = os.path.join(MOCARABE_ROOT, "llvm-with-clang.sh")
PLUGIN = os.path.join(MOCARABE_ROOT, "llvm_pass", "dfg_to_hgr.so")


def requires_plugin():
    return pytest.mark.skipif(
        not os.path.exists(PLUGIN),
        reason="dfg_to_hgr.so not built — run: make -C llvm_pass",
    )


def run_extractor(c_file, out_dir):
    """Run llvm-with-clang.sh and return the completed process."""
    return subprocess.run(
        [SCRIPT, c_file, out_dir],
        capture_output=True,
        text=True,
        cwd=MOCARABE_ROOT,
    )


def hgr_path(out_dir, benchmark):
    return os.path.join(out_dir, benchmark, f"{benchmark}.hgr")


# ---------------------------------------------------------------------------
# Argument validation (no plugin needed)
# ---------------------------------------------------------------------------

def test_no_args_exits_nonzero():
    r = subprocess.run([SCRIPT], capture_output=True, text=True, cwd=MOCARABE_ROOT)
    assert r.returncode != 0


def test_one_arg_exits_nonzero():
    r = subprocess.run(
        [SCRIPT, os.path.join(BENCH_DIR, "int_adder_chain.c")],
        capture_output=True, text=True, cwd=MOCARABE_ROOT,
    )
    assert r.returncode != 0


def test_usage_message_on_missing_args():
    r = subprocess.run([SCRIPT], capture_output=True, text=True, cwd=MOCARABE_ROOT)
    assert "Usage" in r.stderr


# ---------------------------------------------------------------------------
# HGR generation (requires built plugin)
# ---------------------------------------------------------------------------

BENCHMARKS = [
    "int_adder_chain",
    "int_poly_quadratic",
    "int_dct",
    "int_sobel",
    "int_iir8",
    "int_bellido",
]


@requires_plugin()
@pytest.mark.parametrize("benchmark", BENCHMARKS)
def test_hgr_generated(benchmark, tmp_path):
    c_file = os.path.join(BENCH_DIR, f"{benchmark}.c")
    r = run_extractor(c_file, str(tmp_path))
    assert r.returncode == 0, f"extractor failed:\n{r.stderr}"
    assert os.path.exists(hgr_path(str(tmp_path), benchmark))


@requires_plugin()
@pytest.mark.parametrize("benchmark", BENCHMARKS)
def test_hgr_loads_as_netlist(benchmark, tmp_path):
    c_file = os.path.join(BENCH_DIR, f"{benchmark}.c")
    run_extractor(c_file, str(tmp_path))
    path = hgr_path(str(tmp_path), benchmark)
    netlist = Netlist(path)
    assert len(netlist.get_node_set()) > 0
    assert len(netlist.get_hyperedge_id_set()) > 0


@requires_plugin()
@pytest.mark.parametrize("benchmark", BENCHMARKS)
def test_hgr_has_arithmetic_nodes(benchmark, tmp_path):
    c_file = os.path.join(BENCH_DIR, f"{benchmark}.c")
    run_extractor(c_file, str(tmp_path))
    netlist = Netlist(hgr_path(str(tmp_path), benchmark))
    arith = netlist.extract_node_arithmetic_operators()
    assert len(arith) > 0, "Expected at least one arithmetic (+/*) node"


@requires_plugin()
@pytest.mark.parametrize("benchmark", BENCHMARKS)
def test_hgr_has_io_nodes(benchmark, tmp_path):
    c_file = os.path.join(BENCH_DIR, f"{benchmark}.c")
    run_extractor(c_file, str(tmp_path))
    netlist = Netlist(hgr_path(str(tmp_path), benchmark))
    io = netlist.extract_node_io_operators()
    assert len(io) > 0, "Expected at least one IO (input/output/constant) node"


@requires_plugin()
@pytest.mark.parametrize("benchmark,expected_nodes,expected_nets", [
    ("int_adder_chain",    8,  7),
    ("int_poly_quadratic", 9,  8),
    ("int_dct",           77, 69),
])
def test_hgr_node_net_counts(benchmark, expected_nodes, expected_nets, tmp_path):
    c_file = os.path.join(BENCH_DIR, f"{benchmark}.c")
    run_extractor(c_file, str(tmp_path))
    netlist = Netlist(hgr_path(str(tmp_path), benchmark))
    assert len(netlist.get_node_set()) == expected_nodes
    assert len(netlist.get_hyperedge_id_set()) == expected_nets
