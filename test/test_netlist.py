import os
import pytest
from mocarabe.cad.netlist import Netlist

HGR_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "hgr")


@pytest.fixture
def adder_chain():
    """Linear chain: x+y+z+a → ret  (4 IO inputs, 3 adders, 1 output)"""
    return Netlist(
        dfg_path=os.path.join(HGR_ROOT, "int_adder_chain", "int_adder_chain.hgr")
    )


@pytest.fixture
def poly_quadratic():
    """x*x*c + 5 + 1 → y  (fanout on x, mixed IO/arith)"""
    return Netlist(
        dfg_path=os.path.join(HGR_ROOT, "int_poly_quadratic", "int_poly_quadratic.hgr")
    )


# ── basic structure ──────────────────────────────────────────────────────────


def test_node_and_edge_counts(adder_chain):
    assert adder_chain.number_of_vertices == 8
    assert adder_chain.number_of_hedges == 7
    assert len(adder_chain.get_node_set()) == 8
    assert len(adder_chain.get_hyperedge_id_set()) == 7


def test_node_labels(adder_chain):
    labels = {
        adder_chain.get_node_attribute(n, "label") for n in adder_chain.get_node_set()
    }
    assert labels == {"+", "x", "y", "z", "a", "ret"}


# ── topology ─────────────────────────────────────────────────────────────────


def test_root_nodes_adder_chain(adder_chain):
    """IO inputs x, y, z, a are never the head of any hyperedge."""
    roots = adder_chain.get_all_root_nodes()
    root_labels = {adder_chain.get_node_attribute(n, "label") for n in roots}
    assert root_labels == {"x", "y", "z", "a"}


def test_leaf_nodes_adder_chain(adder_chain):
    """Only ret is never the tail of any hyperedge."""
    leaves = adder_chain.get_leaf_nodes()
    leaf_labels = {adder_chain.get_node_attribute(n, "label") for n in leaves}
    assert leaf_labels == {"ret"}


def test_root_nodes_poly_quadratic(poly_quadratic):
    roots = poly_quadratic.get_all_root_nodes()
    root_labels = {poly_quadratic.get_node_attribute(n, "label") for n in roots}
    # x feeds two multipliers (fanout); c, 5, 1 are constants
    assert root_labels == {"x", "c", "5", "1"}


# ── operator classification ──────────────────────────────────────────────────


def test_extract_node_operators_adder_chain(adder_chain):
    ops = adder_chain.extract_node_operators()
    op_values = set(ops.values())
    assert op_values == {"+", "IO"}
    io_count = sum(1 for v in ops.values() if v == "IO")
    assert io_count == 5  # x, y, z, a, ret


def test_extract_node_arithmetic_operators(adder_chain):
    arith = adder_chain.extract_node_arithmetic_operators()
    assert all(v == "+" for v in arith.values())
    assert len(arith) == 3


def test_extract_input_nodes(adder_chain):
    inputs = adder_chain.extract_input_nodes()
    input_labels = set(inputs.values())
    assert input_labels == {"x", "y", "z", "a"}


# ── precedence ───────────────────────────────────────────────────────────────


def test_topo_precedence_holds(adder_chain):
    """Inputs must precede the output in topological order."""
    nodes = {
        adder_chain.get_node_attribute(n, "label"): n
        for n in adder_chain.get_node_set()
    }
    assert adder_chain.is_topo_precedent(nodes["x"], nodes["ret"])
    assert adder_chain.is_topo_precedent(nodes["a"], nodes["ret"])


def test_topo_precedence_no_reverse(adder_chain):
    """The output does not precede any input."""
    nodes = {
        adder_chain.get_node_attribute(n, "label"): n
        for n in adder_chain.get_node_set()
    }
    assert not adder_chain.is_topo_precedent(nodes["ret"], nodes["x"])


# ── parent / head / tail queries ─────────────────────────────────────────────


def test_get_parent_nodes_output(adder_chain):
    """ret has exactly one parent adder; get_parent_nodes duplicates it to length 2."""
    nodes = {
        adder_chain.get_node_attribute(n, "label"): n
        for n in adder_chain.get_node_set()
    }
    parents = adder_chain.get_parent_nodes(nodes["ret"])
    assert len(parents) == 2
    parent_labels = {adder_chain.get_node_attribute(p, "label") for p in parents}
    assert parent_labels == {"+"}


def test_node_is_tail_for_input(adder_chain):
    """An IO input node drives exactly one hyperedge."""
    nodes = {
        adder_chain.get_node_attribute(n, "label"): n
        for n in adder_chain.get_node_set()
    }
    edges = adder_chain.node_is_tail_for(nodes["x"])
    assert len(edges) == 1


def test_node_is_head_for_output(adder_chain):
    """ret is the head of exactly one hyperedge."""
    nodes = {
        adder_chain.get_node_attribute(n, "label"): n
        for n in adder_chain.get_node_set()
    }
    edges = adder_chain.node_is_head_for(nodes["ret"])
    assert len(edges) == 1


# ── nx graph projection ──────────────────────────────────────────────────────


def test_to_graph_has_correct_edge_count(adder_chain):
    """DiGraph should have one directed edge per (tail, head) pair in the hgraph."""
    G = adder_chain.G
    assert G.number_of_edges() == 7


def test_to_graph_fanout(poly_quadratic):
    """x fans out to two multiplier nodes — both edges must exist in the DiGraph."""
    nodes = {
        poly_quadratic.get_node_attribute(n, "label"): n
        for n in poly_quadratic.get_node_set()
    }
    x = nodes["x"]
    successors = set(poly_quadratic.G.successors(x))
    assert len(successors) == 2


# ── unroll ───────────────────────────────────────────────────────────────────


def test_unroll_doubles_counts():
    nl = Netlist(
        dfg_path=os.path.join(HGR_ROOT, "int_adder_chain", "int_adder_chain.hgr"),
        unroll_factor=2,
    )
    assert len(nl.get_node_set()) == 16
    assert len(nl.get_hyperedge_id_set()) == 14
