import glob
import os

import pytest

from mocarabe.cad.netlist import Netlist

MOCARABE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def write_hgr(tmp_path, nodes, edges):
    path = tmp_path / "dfg.hgr"
    lines = [f"{len(edges)} {len(nodes)}"]
    lines += [f"{node_id}:{label}" for node_id, label in nodes]
    lines += ["--"] + [" ".join(edge) for edge in edges]
    path.write_text("\n".join(lines) + "\n")
    return Netlist(str(path))


@pytest.mark.parametrize(
    "path", sorted(glob.glob(os.path.join(MOCARABE_ROOT, "hgr/int_*/int_*.hgr")))
)
def test_int_benchmarks_have_no_operatorless_nodes(path):
    assert Netlist(path).extract_operatorless_nodes() == {}


def test_operatorless_node_detected(tmp_path):
    # 'y' is fed by two nets but has no operator
    dfg = write_hgr(tmp_path, [("0", "a"), ("1", "b"), ("2", "y")], [("0", "2"), ("1", "2")])
    assert dfg.extract_operatorless_nodes() == {"2": "y"}
