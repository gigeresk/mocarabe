from collections import OrderedDict


def create_placed_netlist(H, dfg_node_to_pe_xy_map, with_attributes=True):

    placed_netlist = []
    for hyperedge_id in H.ordered_hyperedge_id_iterator():
        hyperedge = H.get_hyperedge_attributes(hyperedge_id)

        source = hyperedge["tail"][0]
        xy = dfg_node_to_pe_xy_map[source]
        src = (
            xy[0],
            xy[1],
            int(source),
            H.get_node_attribute(source, "label"),
            hyperedge_id,
        )

        sinks = []

        # in the case of a node with the same two inputs (e.g. x = y*y), only one will be routed (which is good)
        unique_sink_ids = list(OrderedDict.fromkeys(hyperedge["head"]))
        for sink in unique_sink_ids:
            xy = dfg_node_to_pe_xy_map[sink]

            sinks.append((xy[0], xy[1], int(sink), H.get_node_attribute(sink, "label")))

        placed_netlist.append((src, sinks))
    # import pdb; pdb.set_trace()
    return placed_netlist
