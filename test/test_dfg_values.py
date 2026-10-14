import pytest

from mocarabe.cad.netlist import Netlist
from mocarabe.rtl_gen.pe_memory_gen import get_node_values


def write_hgr(tmp_path, nodes, edges):
    path = tmp_path / "dfg.hgr"
    lines = [f"{len(edges)} {len(nodes)}"]
    lines += [f"{node_id}:{label}" for node_id, label in nodes]
    lines += ["--"] + [" ".join(edge) for edge in edges]
    path.write_text("\n".join(lines) + "\n")
    return Netlist(str(path))


def test_int_benchmarks_have_no_operatorless_nodes(int_dfg_path):
    assert Netlist(str(int_dfg_path)).extract_operatorless_nodes() == {}


def test_operatorless_node_detected(tmp_path):
    # 'y' is fed by two nets but has no operator
    dfg = write_hgr(tmp_path, [("0", "a"), ("1", "b"), ("2", "y")], [("0", "2"), ("1", "2")])
    assert dfg.extract_operatorless_nodes() == {"2": "y"}


def test_values_wrap_at_data_width(tmp_path):
    dfg = write_hgr(
        tmp_path,
        [("0", "a"), ("1", "b"), ("2", "*"), ("3", "y")],
        [("0", "2"), ("1", "2"), ("2", "3")],
    )
    values = get_node_values({"0": 2**20, "1": 2**20 + 3}, dfg)
    assert values["2"] == (2**20 * (2**20 + 3)) % 2**32


def test_unresolvable_node_raises(tmp_path):
    # 'y' has two inputs but no operator, so '+' downstream can never be computed
    dfg = write_hgr(
        tmp_path,
        [("0", "a"), ("1", "b"), ("2", "y"), ("3", "c"), ("4", "+"), ("5", "z")],
        [("0", "2"), ("1", "2"), ("2", "4"), ("3", "4"), ("4", "5")],
    )
    with pytest.raises(ValueError, match="cannot compute values"):
        get_node_values({"0": 1, "1": 2, "3": 3}, dfg)


def test_split_input_fanout(tmp_path):
    # x feeds '+' and '*' (twice, as x*x); c feeds '+' only
    path = tmp_path / "dfg.hgr"
    path.write_text(
        "4 5\n0:x\n1:c\n2:+\n3:*\n4:y\n--\n0 2 3 3\n1 2\n2 4\n3 4\n"
    )
    dfg = Netlist(str(path), split_input_fanout=True)
    nets = dfg.ordered_hyperedge_id_list()
    assert nets == [f"e{i + 1}" for i in range(len(nets))]
    label = lambda node: dfg.get_node_attribute(node, "label")
    by_tail = {
        label(dfg.get_hyperedge_attribute(net, "tail")[0]): sorted(
            label(head) for head in dfg.get_hyperedge_attribute(net, "head")
        )
        for net in nets
    }
    assert by_tail["x"] == ["+"]
    assert by_tail["x_1"] == ["*", "*"]  # x*x keeps both ports on one copy
    assert by_tail["c"] == ["+"]
