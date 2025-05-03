from collections import OrderedDict


def serialize_placed_netlist(H, dfg_node_to_pe_xy_map, with_attributes=True):

    serialized_placed_netlist = ""
    for hyperedge_id in H.ordered_hyperedge_id_iterator():

        hyperedge = H.get_hyperedge_attributes(
            hyperedge_id)  # TODO do this on unrolledH //todo

        source = hyperedge['tail'][0]
        xy = dfg_node_to_pe_xy_map[source]
        net = "({0},{1},{2},'{3},{4}')".format(xy[0], xy[1], int(
            source), H.get_node_attribute(source, 'label'), hyperedge_id)

        # in the case of a node with the same two inputs (e.g. x = y*y), only one will be routed (which is good)
        unique_sink_ids = list(OrderedDict.fromkeys(hyperedge['head']))
        for sink in unique_sink_ids:
            xy = dfg_node_to_pe_xy_map[sink]
            net = net + ",({0},{1},{2},'{3}')".format(
                xy[0], xy[1], int(sink), H.get_node_attribute(sink, 'label'), )

        # if with_attributes:
        #     if hyperedge['label'] != '':
        #         net = net + " #label{" + hyperedge['label'] + "}"
        serialized_placed_netlist = serialized_placed_netlist + net + "\n"

    return serialized_placed_netlist
