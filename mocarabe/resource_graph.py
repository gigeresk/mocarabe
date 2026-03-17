import networkx as nx
import itertools

from mocarabe.resource_type import ResourceType


class ResourceGraph(nx.DiGraph):
    # TODO II constraints
    # TODO some kind of graph freezing

    def __init__(self):
        super(ResourceGraph, self).__init__()

    def create(self, device):
        self.Nx = device.Nx
        self.Ny = device.Ny

        self.physical_channels = device.physical_channels
        self.schedule_length = device.T
        self.T = device.T
        Nx = self.Nx
        Ny = self.Ny
        # channel_count = device.physical_channels
        pe = {}
        pe_in = {}
        pe_in_port = {}
        pe_in_switch = {}

        pe_out = {}
        pe_out_port = {}
        pe_out_switch = {}

        h_noc = {}
        v_noc = {}
        switch_n = {}
        switch_e = {}

        X_OFFSET = 3 + device.physical_channels
        Y_OFFSET = 3 + device.physical_channels

        IO_O = device.IO_O
        self.IO_O = IO_O
        print(f'IO_O: {IO_O}')
        IO_I = device.IO_I
        self.IO_I = IO_I
        print(f'IO_I: {IO_I}')
        def node_count(c=itertools.count()): return next(c)
        for x in range(device.Nx):
            for y in range(device.Ny):
                node_cnt = node_count()
                # PE
                self.add_node(node_cnt, params=(x, y), pos=(
                    x*X_OFFSET, y*Y_OFFSET), type=ResourceType.PE, label=f"PE")
                pe[(x, y)] = node_cnt

                for t in range(device.schedule_length):
                    # pe_out, at an (x,y,t) position ( feeding into all output ports)
                    # TOFIX C>1
                    node_cnt = node_count()
                    self.add_node(node_cnt, params=(x, y, t), pos=(
                        x*X_OFFSET, y*Y_OFFSET+1),  cycle=t, type=ResourceType.PE_OUT, label=f"pe_out")
                    pe_out[(x, y, t)] = node_cnt
                    for io_o in range(IO_O):
                        node_cnt = node_count()
                        self.add_node(node_cnt, params=(x, y, io_o, t), pos=(
                            x*X_OFFSET, y*Y_OFFSET+1),  cycle=t, type=ResourceType.PE_OUT_PORT, label=f"pe_out")
                        pe_out_port[(x, y, io_o, t)] = node_cnt
                    # pe_in
                    # TOFIX C>1
                    # IO_O
                    node_cnt = node_count()
                    self.add_node(node_cnt, params=(x, y, t), pos=(
                        x*X_OFFSET+1, y*Y_OFFSET),  cycle=t, type=ResourceType.PE_IN, label=f"pe_in")
                    pe_in[(x, y, t)] = node_cnt
                    for io_i in range(IO_I):
                        node_cnt = node_count()
                        self.add_node(node_cnt, params=(x, y, io_i, t), pos=(
                            x*X_OFFSET+1, y*Y_OFFSET),  cycle=t, type=ResourceType.PE_IN_PORT, label=f"pe_in")
                        pe_in_port[(x, y, io_i, t)] = node_cnt

                    # for c in range(device.physical_channels-1,-1,-1): # no idea why
                    for c in range(device.physical_channels):
                        # H_NOC
                        node_cnt = node_count()
                        self.add_node(node_cnt, params=(x, y, c, t), pos=(
                            x*X_OFFSET+1, y*Y_OFFSET+2+c),  cycle=t, type=ResourceType.H_NOC, label=f"h")
                        h_noc[(x, y, c, t)] = node_cnt
                        # V_NOC
                        node_cnt = node_count()
                        self.add_node(node_cnt, params=(x, y, c, t), pos=(
                            x*X_OFFSET+2+c, y*Y_OFFSET),  cycle=t, type=ResourceType.V_NOC, label=f"v")
                        v_noc[(x, y, c, t)] = node_cnt
                        # SWITCH_N
                        node_cnt = node_count()
                        self.add_node(node_cnt, params=(x, y, c, t), pos=(
                            x*X_OFFSET+2+c, y*Y_OFFSET+2+c),  cycle=t, type=ResourceType.SWITCH_N, label=f"swN")
                        switch_n[(x, y, c, t)] = node_cnt
                        # SWITCH_E
                        node_cnt = node_count()
                        self.add_node(node_cnt, params=(x, y, c, t), pos=(
                            x*X_OFFSET+2, y*Y_OFFSET+1+c),  cycle=t, type=ResourceType.SWITCH_E, label=f"swE")
                        switch_e[(x, y, c, t)] = node_cnt

                        # pe_in_switch
                        node_cnt = node_count()
                        self.add_node(node_cnt, params=(x, y, c, t), pos=(
                            x*X_OFFSET+1, y*Y_OFFSET+1),  cycle=t, type=ResourceType.PE_IN_SWITCH, label=f"swPEin")
                        pe_in_switch[(x, y, c, t)] = node_cnt

                        # pe_out_switch
                        node_cnt = node_count()
                        self.add_node(node_cnt, params=(x, y, c, t), pos=(
                            x*X_OFFSET+1, y*Y_OFFSET+1),  cycle=t, type=ResourceType.PE_OUT_SWITCH, label=f"swPEout")
                        pe_out_switch[(x, y, c, t)] = node_cnt

        # PE(x,y)
        # PE_in(x,y,t)
        # PE_in_port(x,y,io_i,t) # these two are needed
        # PE_in_switch(x,y,c,t) # to prepare for fewer IO_I ports

        # connectivity
        for t in range(device.schedule_length):
            next_t = (t+1) % device.schedule_length
            next_t_noc = (
                t+1+device.noc_pipelining_stages) % device.schedule_length
            next_t_pe = (
                t+1+device.pe_pipelining_stages) % device.schedule_length

            for x in range(device.Nx):
                for y in range(device.Ny):

                    self.add_edge(pe[(x, y)], pe_out[(x, y, t)])
                    for io_o in range(IO_O):
                        self.add_edge(pe_out[(x, y, t)],
                                      pe_out_port[(x, y, io_o, t)])

                    for c in range(device.physical_channels):
                        self.add_edge(
                            pe_out_port[(x, y, io_o, t)], pe_out_switch[(x, y, c, t)])

                    # self.add_edge( h[(x,y,t)], pe_in[x,y,t])
                    self.add_edge(pe_in[(x, y, t)], pe[(x, y)])
                    for io_i in range(IO_I):
                        self.add_edge(
                            pe_in_port[(x, y, io_i, t)], pe_in[(x, y, t)])

                    for c in range(device.physical_channels):
                        # to V_NOC (NORTH)
                        self.add_edge(
                            pe_out_switch[(x, y, c, t)], v_noc[(x, (y+1) % Ny, c, next_t)])
                        self.add_edge(v_noc[(x, y, c, t)], v_noc[(
                            x, (y+1) % Ny, c, next_t_noc)])
                        self.add_edge(h_noc[(x, y, c, t)], v_noc[(
                            x, (y+1) % Ny, c, next_t_noc)])

                        # to H_NOC (EAST)
                        self.add_edge(
                            pe_out_switch[(x, y, c, t)], h_noc[(x+1) % Nx, y, c, next_t])
                        self.add_edge(v_noc[(x, y, c, t)],
                                      h_noc[(x+1) % Nx, y, c, next_t_noc])
                        self.add_edge(h_noc[(x, y, c, t)],
                                      h_noc[(x+1) % Nx, y, c, next_t_noc])

                        # to pe_in_switch
                        self.add_edge(v_noc[(x, y, c, t)],
                                      pe_in_switch[(x, y, c, next_t)])
                        self.add_edge(h_noc[(x, y, c, t)],
                                      pe_in_switch[(x, y, c, next_t)])

                        # to pe_in_port
                        # TODO is this also pipelined
                        # TODO for greater # channels
                        for io_i in range(IO_I):  # TODO is this too many links?
                            # Bottleneck C down to IO_I, if necessary.
                            # TODO This is a bit tricky... Deal with this explicitly
                            # if c == io_i:
                            self.add_edge(
                                pe_in_switch[(x, y, c, t)], pe_in_port[(x, y, io_i, t)])
                            self.add_edge(
                                pe_in_switch[(x, y, c, t)], pe_in_port[(x, y, io_i, t)])

        self.pe = pe
        self.pe_in = pe_in
        self.pe_out = pe_out
        self.h_noc = h_noc
        self.v_noc = v_noc
        self.switch_n = switch_n
        self.switch_e = switch_e
        self.pe_in_switch = pe_in_switch
        self.pe_out_switch = pe_out_switch

        self.pe_in_port = pe_in_port
        self.pe_out_port = pe_out_port
        self.pe_in_nodes = []
        for node in self.pe_in.values():
            self.pe_in_nodes.append(node)

        self.pe_in_port_nodes = []
        for node in self.pe_in_port.values():
            self.pe_in_port_nodes.append(node)

        self.pe_nodes = []
        for node in self.pe.values():
            self.pe_nodes.append(node)

        self.node_attributes_params = nx.get_node_attributes(self, 'params')
        self.node_attributes_type = nx.get_node_attributes(self, 'type')

    def node_to_resource(self, node) -> str:

        node_type = self.node_attributes_type[node]
        node_pos = self.node_attributes_params[node]

        if node_type == ResourceType.PE:
            return f"PE at ({node_pos[0]},{node_pos[1]}) [{node}]"
        elif node_type == ResourceType.PE_IN:
            return f"PE_in at ({node_pos[0]},{node_pos[1]}), t={node_pos[2]} [{node}]"
        elif node_type == ResourceType.PE_IN_PORT:
            return f"PE_in_port at ({node_pos[0]},{node_pos[1]}), io={node_pos[2]}, t={node_pos[3]} [{node}]"
        elif node_type == ResourceType.PE_OUT:
            return f"PE_out at ({node_pos[0]},{node_pos[1]}), t={node_pos[2]} [{node}]"
        elif node_type == ResourceType.PE_OUT_PORT:
            return f"PE_out_port at ({node_pos[0]},{node_pos[1]}), io={node_pos[2]}, t={node_pos[3]} [{node}]"
        elif node_type == ResourceType.H_NOC:
            return f"h at ({node_pos[0]},{node_pos[1]}), c={node_pos[2]}, t={node_pos[3]} [{node}]"
        elif node_type == ResourceType.V_NOC:
            return f"v at ({node_pos[0]},{node_pos[1]}), c={node_pos[2]}, t={node_pos[3]} [{node}]"
        elif node_type == ResourceType.SWITCH_N:
            return f"swN at ({node_pos[0]},{node_pos[1]}), c={node_pos[2]}, t={node_pos[3]} [{node}]"
        elif node_type == ResourceType.SWITCH_E:
            return f"swE at ({node_pos[0]},{node_pos[1]}), c={node_pos[2]}, t={node_pos[3]} [{node}]"
        elif node_type == ResourceType.PE_IN_SWITCH:
            return f"PE_in_switch at ({node_pos[0]},{node_pos[1]}), c={node_pos[2]}, t={node_pos[3]} [{node}]"
        elif node_type == ResourceType.PE_OUT_SWITCH:
            return f"PE_out_switch at ({node_pos[0]},{node_pos[1]}), c={node_pos[2]}, t={node_pos[3]} [{node}]"
        else:
            return "untracked"

    def nodes_to_resources(self, nodes):
        ret = []
        for node in nodes:
            ret.append(self.node_to_resource(node))
        return ret

    def node_to_old_style(self, node, connectionid):

        node_type = self.node_attributes_type[node]
        node_pos = self.node_attributes_params[node]

        # if node_type == ResourceType.PE_IN:
        #     return f"exit___[{node_pos[0]}][{node_pos[1]}][0][{connectionid}][{node_pos[2]}] = 1\n"
        # el
        if node_type == ResourceType.PE_OUT_SWITCH:
            return f"enter[{node_pos[0]}][{node_pos[1]}][{node_pos[2]}][{connectionid}][{node_pos[3]}] = 1\n"
        elif node_type == ResourceType.H_NOC:
            return f"h[{node_pos[0]}][{node_pos[1]}][{node_pos[2]}][{connectionid}][{node_pos[3]}] = 1\n"
        elif node_type == ResourceType.V_NOC:
            return f"v[{node_pos[0]}][{node_pos[1]}][{node_pos[2]}][{connectionid}][{node_pos[3]}] = 1\n"
        elif node_type == ResourceType.PE_IN_SWITCH:
            return f"exit[{node_pos[0]}][{node_pos[1]}][{node_pos[2]}][{connectionid}][{node_pos[3]}] = 1\n"
        else:
            return ''

    def getxy(self, node):
        node_params = self.node_attributes_params[node]
        return (node_params[0], node_params[1])
