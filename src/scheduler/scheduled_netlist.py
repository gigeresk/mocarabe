from src.resource_graph import ResourceGraph
from src.resource_type import ResourceType


class ScheduledNetlist:
    # print
    # dfg-awareness
    # logical to physical awareness?
    # common interface for pf scheduler, resource graph, etc.
    def __init__(self, resource_graph):
        self.netlist = []
        self.resource_graph = resource_graph
        pass

    def append(self, scheduled_net):
        self.netlist.append(scheduled_net)

    def __str__(self):
        netlist_string = ""
        for net in self.netlist:
            # enter
            netlist_string += self.resource_graph.node_to_old_style(
                net.enter_noc, net.id)

            for noc_hop in net.noc_hops:
                netlist_string += self.resource_graph.node_to_old_style(
                    noc_hop, net.id)

            for exit_ in net.exit_noc:
                netlist_string += self.resource_graph.node_to_old_style(
                    exit_, net.id)

        return netlist_string

    def physical_channel_utilization(self, Nx, Ny, physical_channels, T):
        h_channel_utilization = [
            [[0 for t in range(T)] for y in range(Ny)] for x in range(Nx)]
        v_channel_utilization = [
            [[0 for t in range(T)] for y in range(Ny)] for x in range(Nx)]

        self.resource_graph.node_attributes_params
        self.resource_graph.node_attributes_type

        for net in self.netlist:
            for noc_node in net.noc_hops:
                x, y, c, t = [
                    *self.resource_graph.node_attributes_params[noc_node]]

                if (self.resource_graph.node_attributes_type[noc_node] == ResourceType.H_NOC):
                    h_channel_utilization[x][y][t] += 1
                elif (self.resource_graph.node_attributes_type[noc_node] == ResourceType.V_NOC):
                    v_channel_utilization[x][y][t] += 1
        return h_channel_utilization, v_channel_utilization

    def physical_channel_utilization_factor(self, Nx, Ny, physical_channels, T):
        h_channel_utilization, v_channel_utilization = self.physical_channel_utilization(
            Nx, Ny, physical_channels, T)

        total = 2 * Nx * Ny * physical_channels * T
        used = 0
        for x in range(Nx):
            for y in range(Ny):
                for t in range(T):
                    used += h_channel_utilization[x][y][t]
                    used += v_channel_utilization[x][y][t]
        return used / total

    def unused_xy(self, Nx, Ny, physical_channels, T):
        h_channel_utilization, v_channel_utilization = self.physical_channel_utilization(
            Nx, Ny, physical_channels, T)
        h_channel_used = [[0 for y in range(Ny)] for x in range(Nx)]
        v_channel_used = [[0 for y in range(Ny)] for x in range(Nx)]

        for x in range(Nx):
            for y in range(Ny):
                h_channel_used[x][y] = sum(h_channel_utilization[x][y])
                v_channel_used[x][y] = sum(v_channel_utilization[x][y])

        num_unused = 0
        for x in range(Nx):
            for y in range(Ny):
                if h_channel_used[x][y] == 0:

                    num_unused += 1
                if v_channel_used[x][y] == 0:
                    num_unused += 1
        return num_unused / (2*Nx*Ny)
