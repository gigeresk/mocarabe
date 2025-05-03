import re


def parseIndices(l):
    indexRegex = re.compile('(?<=\[)\d*(?=\])')
    enter = indexRegex.findall(l)
    indices = [int(x) for x in enter]
    return indices


def maxT(filename):
    solfile = open(filename, 'r')

    TMax = 0
    currentT = 0
    for line in solfile:
        match = re.compile('\d*(?=(] = 1$))').search(line)
        if match:
            currentT = int(match.group())
        if (currentT > TMax):
            TMax = currentT
    solfile.close()
    return TMax


class RTLGenerator:
    ''' TODO
    global_node_enter_cycle, global_node_enter_cycle: these should both be arrays...
    however, being dicts really helps with debugging for now

    '''

    from .header_gen import verilog_header_gen
    from .noc_mux_memory_gen import generate_and_write_noc_mux_memories
    from .pe_memory_gen import get_net_path_nodes, generate_and_write_pe_memories
    from .testbench_gen import testbench_gen

    @staticmethod
    def deserialize_schedule(sched_filename, Nx, Ny, C, P, T):

        h = [[[[[0 for t in range(T)] for p in range(P)] for c in range(
            C)] for y in range(Ny)] for x in range(Nx)]
        v = [[[[[0 for t in range(T)] for p in range(P)] for c in range(
            C)] for y in range(Ny)] for x in range(Nx)]
        enter = [[[[[0 for t in range(T)] for p in range(P)] for c in range(
            C)] for y in range(Ny)] for x in range(Nx)]
        exit_ = [[[[[0 for t in range(T)] for p in range(P)] for c in range(
            C)] for y in range(Ny)] for x in range(Nx)]

        with open(sched_filename) as f:
            lines = f.read().splitlines()
        for l in lines:
            if len(l) == 0:
                continue
            ind = parseIndices(l)

            if l[0] == 'h':
                h[ind[0]][ind[1]][ind[2]][ind[3]][ind[4]] = int(l[-1])
            elif l[0] == 'v':
                v[ind[0]][ind[1]][ind[2]][ind[3]][ind[4]] = int(l[-1])
            elif l[0:6] != 'enterc' and l[0:5] == 'enter':
                enter[ind[0]][ind[1]][ind[2]][ind[3]][ind[4]] = int(l[-1])
            elif l[0:5] != 'exitc' and l[0:4] == 'exit':
                exit_[ind[0]][ind[1]][ind[2]][ind[3]][ind[4]] = int(l[-1])
            else:
                continue

        T = maxT(sched_filename) + 1

        return h, v, enter, exit_, T
