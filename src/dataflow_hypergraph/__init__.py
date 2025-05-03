from halp.directed_hypergraph import DirectedHypergraph


class DataflowHypergraph(DirectedHypergraph):
    def __init__(self, dfg_path='', unroll_factor=1):

        super(DataflowHypergraph, self).__init__()
        self.number_of_hedges = 0
        self.number_of_vertices = 0

        self.name = ""
        if dfg_path != '':
            self.deserialize_df_hypergraph(dfg_path)
            self.unroll_dfg(unroll_factor)

    from ._dataflow_hypergraph import serialize_df_hypergraph, deserialize_df_hypergraph, unroll_dfg
    from ._dataflow_hypergraph import num_retiming_registers
    from ._dataflow_hypergraph import to_graph, to_dot
    from ._dataflow_hypergraph import extract_labels, extract_node_operators, extract_node_arithmetic_operators, extract_node_io_operators, extract_input_nodes, extract_output_nodes
    from ._dataflow_hypergraph import ordered_hyperedge_id_list, ordered_hyperedge_id_iterator, get_predecessors
    from ._dataflow_hypergraph import ordered_node_id_list, ordered_node_id_iterator, is_topo_precedent, get_leaf_nodes, get_all_root_nodes
    from ._dataflow_hypergraph import node_is_head_for, node_is_tail_for, get_sibling_operands, get_parent_nodes
