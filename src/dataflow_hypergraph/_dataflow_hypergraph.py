
import collections  # for OrderedDict

import networkx as nx
import palettable
# try:
#     import networkx as nx
# except:
#     print("pip3 install networkx")
# try:
#     import palettable
# except:
#     print("pip3 install palettable")

from halp.directed_hypergraph import DirectedHypergraph
from halp.utilities import directed_statistics
from networkx.algorithms.dag import topological_sort
from networkx.algorithms.shortest_paths.generic import has_path


def serialize_df_hypergraph(self, H: DirectedHypergraph, path: str) -> None:
    '''
    # number of hyperedges, number of vertices
    5 6
    # hypergraph node labels
    1: x
    0: *
    3: +
    2: 2
    4: +
    5: value
    -- # hyperedges
    1 0 3 # node 1 (x) will get multiplied at node 0, added at node 3 (fanout=2)
    2 0 0 # self-multiply
    0 4
    3 4
    4 5
    '''
    '''
    Note on self-operating node (e.g. 2 0 0, which means node 0 = node 2 * node 2 as in example above)
    2->0 should only be routed once, but rtl_gen should be correct
    '''

    dfg_file = open(path, "w+")

    # first line of the file: hyperedge count, node count
    hgr_header = "{0} {1}".format(
        len(H.get_hyperedge_id_set()), len(H.get_node_set()))
    dfg_file.write("{0}\n".format(hgr_header))

    # vertices
    for node_id in H.node_iterator():
        node_label = H.get_node_attribute(node_id, 'label')
        dfg_file.write(str(node_id) + ':' + str(node_label) + '\n')

    dfg_file.write("--\n")
    # hyperedges
    for edge in H.hyperedge_id_iterator():
        hyperedge = H.get_hyperedge_attributes(edge)
        assert (len(hyperedge['tail']) ==
                1), "DFG hyperedges can only have one source ('tail' attribute)"

        line = hyperedge['tail'][0] + " "
        for head in hyperedge['head']:
            line = line + head + ' '
        dfg_file.write("{0}\n".format(line))

    dfg_file.close()


def deserialize_df_hypergraph(self, path: str) -> DirectedHypergraph:

    finished_parsing_vertices = False
    with open(path, 'r') as fp:
        for line_count, line in enumerate(fp):
            if line_count == 0:
                self.number_of_hedges = int(line.split(" ")[0])
                self.number_of_vertices = int(line.split(" ")[1])

            elif '--' in line:
                finished_parsing_vertices = True
            elif not finished_parsing_vertices:
                node_line = line.split('#')[0].strip()  # comments
                node_id, label = node_line.split(
                    ':')[0].strip(), node_line.split(':')[1].strip()
                self.add_node(node_id, label=label)
            elif finished_parsing_vertices:
                edge_list = line.partition('#')[0]  # comments

                vertices = [node for node in edge_list.split()
                            if node.isdigit()]

                '''1 0 3 # node 1 (x) will get multiplied at node 0, added at node 3 (fanout=2)'''
                source = vertices[0]
                sinks = vertices[1:]

                self.add_hyperedge([source], sinks)

    assert (self.number_of_hedges == len(self.get_hyperedge_id_set())
            ), 'Hyperedge count inconsistent with file header'
    assert (self.number_of_vertices == len(self.get_node_set())
            ), 'node count inconsistent with file header'

    self.dataflow_graph = self

    self.G = self.to_graph()  # precompute this (nx Graph)
    return self


def extract_node_operators(self):
    operators = {}
    for node_id in self.ordered_node_id_iterator():
        label = self.get_node_attribute(node_id, 'label')

        if label[0].isalpha() or label.isnumeric():
            operators[node_id] = 'IO'
        else:
            operators[node_id] = label
    return operators


def extract_node_arithmetic_operators(self):
    operators = {}
    for node_id in self.ordered_node_id_iterator():
        label = self.get_node_attribute(node_id, 'label')

        if not label[0].isalpha() and not label.lstrip('-').isnumeric():
            operators[node_id] = label
    return operators


def extract_input_nodes(self):
    # must not be on the end of anything
    input_nodes = {}
    for hyperedge_id in self.ordered_hyperedge_id_iterator():
        hyperedge = self.get_hyperedge_attributes(hyperedge_id)
        tail_id = hyperedge['tail'][0]
        tail_label = self.get_node_attribute(tail_id, 'label')
        if tail_label.lstrip('-').isdigit() or tail_label.isidentifier():
            input_nodes[tail_id] = tail_label
    return input_nodes


def extract_output_nodes(self):
    # must not be on the end of anything
    output_nodes = {}
    for hyperedge_id in self.ordered_hyperedge_id_iterator():
        hyperedge = self.get_hyperedge_attributes(hyperedge_id)
        for head_id in hyperedge['head']:

            head_label = self.get_node_attribute(head_id, 'label')

        if head_label.isnumeric() or head_label.isidentifier():
            output_nodes[head_id] = head_label

    return output_nodes


def extract_node_io_operators(self):
    # hmm.. if it's a sink, then it's IO_O
    operators = {}
    for node_id in self.ordered_node_id_iterator():
        label = self.get_node_attribute(node_id, 'label')

        if label[0].isnumeric() or label.isidentifier():
            operators[node_id] = 'IO'
    return operators


def extract_labels(self):
    labels = []
    for node_id in self.ordered_node_id_iterator():
        labels.append(self.get_node_attribute(node_id, 'label'))

    return labels


def unroll_dfg(self, unroll_factor: int):
    '''
    With a factor of 1, serves as a 'copy constructor'
    '''
    # if type(H) == Di
    # unrolled_H = self

    initial_node_set = self.get_node_set()
    initial_hyperedge_id_set = self.get_hyperedge_id_set()
    ordered_hyperedge_id_list = self.ordered_hyperedge_id_list()

    num_of_vertices = len(self.get_node_set())
    for loop_num in range(unroll_factor):
        for h_edge_id in ordered_hyperedge_id_list:
            hyperedge = self.get_hyperedge_attributes(h_edge_id)

            assert (len(
                hyperedge['tail']) <= 1), "DFG hyperedges can only have one source ('tail' attribute)"
            src = hyperedge['tail'][0]
            sinks = hyperedge['head']
            # For use with (e.g.) hmetis, add (loop_num * number of vertices) instead

            '''Label unrolled vertices by appending 'U-<loop_num>'
            '''
            # loop_src = src + "U" + str(loop_num) if loop_num > 0 else src
            loop_src = str(int(src) + loop_num * num_of_vertices)

            if loop_src not in self.get_node_set():
                label = self.get_node_attribute(src, 'label')
                self.add_node(loop_src, label=label)

            loop_sinks = []
            for sink in sinks:
                # loop_sink = sink + "U" + str(loop_num) if loop_num > 0 else sink
                loop_sink = str(int(sink) + loop_num * num_of_vertices)
                if loop_sink not in self.get_node_set():
                    label = self.get_node_attribute(sink, 'label')
                    self.add_node(loop_sink, label=label)

                loop_sinks.append(loop_sink)

            self.add_hyperedge([loop_src],
                               loop_sinks
                               )

    assert (len(self.get_node_set()) == unroll_factor * len(initial_node_set))
    assert (len(self.get_hyperedge_id_set()) ==
            unroll_factor * len(initial_hyperedge_id_set))
    self.G = self.to_graph()  # precompute this
    return


def num_retiming_registers(self) -> int:
    # get maxDepth for each node, from each input
    # TODO broken
    idgl = directed_statistics.indegree_list(self)
    maxDepth = {}
    for item, node in enumerate(self.get_node_set()):
        if idgl[item] != 0:
            continue
        maxDepth[node] = 0  # input vertices
        node_depths = self.__get_successor_depth_levels(node, 0)

        for successor, depth in node_depths.items():
            if successor in maxDepth.keys():
                if depth > maxDepth[successor]:
                    maxDepth[successor] = depth
            else:
                maxDepth[successor] = depth

    retiming_registers = 0
    idgl = directed_statistics.indegree_list(self)
    # for every hyperedge, what is the greatest depth difference?
    for hyperedge_id in self.ordered_hyperedge_id_list():
        hyperedge = self.get_hyperedge_attributes(hyperedge_id)
        tail_node = hyperedge['tail'][0]
        for head_node in hyperedge['head']:

            # for all input neighbors
            if (maxDepth[head_node] - maxDepth[tail_node] > 1):
                retiming_registers = retiming_registers + \
                    (maxDepth[head_node] - maxDepth[tail_node]) - 1
    return retiming_registers


def __get_successor_depth_levels(self, start, depth) -> dict:
    # get a dict of a starting node's succesors and their depth from the start
    neighbour_depth = {}
    for hyperedge_id in list(self.ordered_hyperedge_id_iterator()):
        hyperedge = self.get_hyperedge_attributes(hyperedge_id)
        if (hyperedge['tail']) == start:
            for neighbour in hyperedge['head']:
                neighbour_depth[neighbour] = depth + 1
                neighbour_depth.update(self.__get_successor_depth_levels(
                    neighbour, neighbour_depth[neighbour]))
    return neighbour_depth


def to_graph(self):
    # halp.utilities.directed_graph_transformations.to_networkx_digraph(H) #TODO
    P_for_node = collections.OrderedDict()

    P = 0

    G = nx.DiGraph()

    for node_id in self.ordered_node_id_iterator():
        label = self.get_node_attribute(node_id, 'label')

        G.add_node(node_id, label=label)

    for hyperedge_id in self.ordered_hyperedge_id_iterator():
        hyperedge = self.get_hyperedge_attributes(hyperedge_id)

        assert (len(hyperedge['tail']) == 1), 'A net may only have one driver.'
        source = hyperedge['tail'][0]

        P_for_node[source] = P

        sinks = hyperedge['head']
        for sink in sinks:
            G.add_edge(source, sink, h_edge=P)
        P = P + 1
    return G


def to_dot(self) -> str:
    from halp.utilities.directed_graph_transformations import to_networkx_digraph
    G = to_networkx_digraph(self)
    # TODO style filled if constant or variable, not operator?
    palette = palettable.tableau.Tableau_20.hex_colors

    name = "benchmark"

    header = 'digraph ' + name + ' {\n'

    node_string = ""

    for node in G.nodes.data():

        node_string = node_string + "    " + node[0] +\
            ' [label ="{0}",fontname="Times-New-Roman", fillcolor="{1}", style="filled"];\n'.format(
                node[1]['label'], palette[int(node[0]) % len(palette)])

    edge_string = ""
    for edge in G.edges.data():
        edge_string = edge_string + '    ' + str(edge[0]) + ' -> ' + str(edge[1]) + \
            ' [color="{}"]'.format(palette[int(edge[0]) % len(palette)]) + '\n'

    result = header + node_string + edge_string + "}\n"
    return result


def ordered_hyperedge_id_list(self):
    return sorted(self.get_hyperedge_id_set(), key=lambda x: (int(x[1:])))


def ordered_hyperedge_id_iterator(self):
    return iter(self.ordered_hyperedge_id_list())


def ordered_node_id_list(self):
    return sorted(self.get_node_set(), key=lambda x: (int(x)))


def ordered_node_id_iterator(self):
    return iter(self.ordered_node_id_list())


def is_topo_precedent(self, node_i: str, node_j: str):
    # G = self.to_graph() # have to precompute this.
    if has_path(self.G, node_i, node_j):
        return True
    else:
        return False


def get_leaf_nodes(self):
    # if a node is never a tail, then it is a leaf

    leaf_candidates = set(self.ordered_node_id_list())

    for root_node in self.get_all_root_nodes():
        leaf_candidates.remove(root_node)

    for hyperedge_id in self.ordered_hyperedge_id_iterator():
        for tail in self.get_hyperedge_attributes(hyperedge_id)['tail']:
            if tail in leaf_candidates:
                leaf_candidates.remove(tail)

    return list(leaf_candidates)


def node_is_head_for(self, node):
    hedges = []
    for hyperedge_id in self.ordered_hyperedge_id_iterator():
        head_nodes = self.get_hyperedge_attributes(hyperedge_id)['head']
        if node in head_nodes:
            hedges.append(hyperedge_id)
    return hedges


def node_is_tail_for(self, node):
    hyperedge_this_node_is_tail_for = set()
    for hyperedge_id in self.ordered_hyperedge_id_iterator():
        tail_nodes = self.get_hyperedge_attributes(hyperedge_id)['tail']
        if node in tail_nodes:
            hyperedge_this_node_is_tail_for.add(hyperedge_id)

    return list(hyperedge_this_node_is_tail_for)


def get_all_root_nodes(self):

    set_of_nodes = set(self.ordered_node_id_list())

    for hyperedge_id in self.ordered_hyperedge_id_iterator():
        head_nodes = self.get_hyperedge_attributes(hyperedge_id)['head']

        for head_node in head_nodes:
            set_of_nodes.discard(head_node)

    return list(set_of_nodes)


def get_predecessors(self, node):
    predecessors = collections.OrderedDict()

    for hyperedge_id in self.ordered_hyperedge_id_iterator():
        head_nodes = self.get_hyperedge_attributes(hyperedge_id)['head']
        for head_node in head_nodes:
            if head_node == node:
                predecessors[hyperedge_id] = None
    return [*predecessors]


def get_sibling_operands(self):
    sibling_operands = [0] * len(self.ordered_node_id_list())
    for ix in range(len(sibling_operands)):
        sibling_operands[ix] = dict()

    for hyperedge_id in self.ordered_hyperedge_id_iterator():
        hyperedge = self.get_hyperedge_attributes(hyperedge_id)
        head_nodes = hyperedge['head']
        for head_node in head_nodes:
            sibling_operands[int(head_node)][hyperedge_id] = None

    return sibling_operands


def get_parent_nodes(self, node):
    # There can be at most two parent nodes
    # 0 if input
    # 1 if output
    # 1 if both operands are the same

    parent_nodes = []

    parent_hyperedges = self.node_is_head_for(node)
    for hyperedge_id in parent_hyperedges:
        hyperedge = self.get_hyperedge_attributes(hyperedge_id)

        assert (len(hyperedge['tail']) ==
                1), "Hyperedges can only have one tail (source) node"

        parent_nodes.append(hyperedge['tail'][0])

    if len(parent_nodes) == 1:
        # If both operands are the same node
        parent_nodes.append(parent_nodes[0])

    return parent_nodes
