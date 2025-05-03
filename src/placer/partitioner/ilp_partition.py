import math
import timeit
from gurobipy import *


def partition_operator(operator_ranges, partition):
    for op, op_range in operator_ranges.items():
        if partition in op_range:
            return op


def partition_with_ilp(HG, K, num_partitions_given_to_operator, partition_filename, II, log_dir='.'):

    VERBOSE = False

    # log_dir = '.'
    '''
    HYPERGRAPH PARTITIONING TECHNIQUES; D. Kucar, S. Areibi, A. Vannelli
    Thank you https://pdfs.semanticscholar.org/7f74/2a66842e333bcf237df0e3a4a575eed4b97b.pdf
    http://www.math.uwaterloo.ca/~xzliu/v11n2-3a/d12kuc.pdf
    The naming conventions here differ slightly from the paper above because I don't
    believe in using k to identify a net and K to mean # of partitions/ways
    partition = 1..K partitions
    v = 1..|V| vertices
    h = 1..|E| hyperedges
    v'= 1..p(h) vertices per hyperedge h
    define x(v,partition)=1 if node v is in partition partition and 0 otherwise
    Thus if a specific net consists of vertices 1 through 4.. uncut if xi1*xi2*xi3*xi4 = 1
    '''
    #     Partition based on arithmetic_operators.
    # Note that operator mapping are based being a sink ( or l-value, depending on how you look at it )
    # So for a = b + c, i.e. b->a, c->a, only 'a' will be in the operator map.
    # If b and c are not the result of a previous computation, they are unconstrained.
    t0 = timeit.default_timer()
    print('--------------Partitioning DFG to pack PEs--------------\n')

    arithmetic_operators = HG.extract_node_arithmetic_operators()
    in_nodes = HG.extract_input_nodes()
    out_nodes = HG.extract_output_nodes()

    operator_ranges = {}
    prevOperatorMax = 0
    for operator, num_of_operators in num_partitions_given_to_operator.items():

        operator_ranges[operator] = range(
            prevOperatorMax, prevOperatorMax + num_of_operators)
        prevOperatorMax = prevOperatorMax + num_of_operators

    H = len(HG.get_hyperedge_id_set())
    V = len(HG.get_node_set())
    netlist = []  # = [0] * H

    for edge in HG.ordered_hyperedge_id_iterator():
        hyperedge = HG.get_hyperedge_attributes(edge)
        driver = hyperedge['tail'][0]
        net = [int(driver)]

        for sink in hyperedge['head']:
            net.append(int(sink))
        netlist.append(net)
    # Create a new model
    m = Model("mip-partition")
    # Create variables
    # x(v,partition) = 1 if node v is in partition *partition*; else 0
    x = m.addVars(V, K, vtype=GRB.BINARY, name='x')
    # y(h,partition) = 1 if net h is entirely in partition *partition(); else 0
    y = m.addVars(H, K, vtype=GRB.BINARY, name='y')
    # (1) Set objective
    m.setObjective(quicksum(y[h, partition] for h in range(
        # sum of cut nets maximized
        H) for partition in range(K)), GRB.MAXIMIZE)
    # (2) every node in exactly one partition
    for v in range(V):
        m.addConstr(quicksum(x[v, partition] for partition in range(K)) == 1)

    # FOR ARITH OPERATIONS
    # (3)a partition size LB
    MIN_ARITH_PARTITION_SIZE = 0
    for partition in range(K):
        if partition_operator(operator_ranges, partition) in ['*', '+']:
            m.addConstr(quicksum(x[v, partition] for v in range(
                V)) >= MIN_ARITH_PARTITION_SIZE)  # TODO can update
    #

    # (3)b partition size UB
    # can't be V/K because we
    #  don't balance things out?
    # math.ceil( V/K) # len(arithmetic_operators) / K ) # TODO can update
    MAX_ARITH_PARTITION_SIZE = 7
    nets_for_each_operator = {}
    for k, v in operator_ranges.items():
        nets_for_each_operator[k] = 0
    #
    for k, v in arithmetic_operators.items():
        nets_for_each_operator[v] = nets_for_each_operator[v] + 1
    #
    # TODO UNCOMMENT
    for partition in range(K):
        MAX_ARITH_PARTITION_SIZE = 10
        # if partition >= operator_ranges['*'][0] and partition <=  operator_ranges['*'][1]:
        if partition_operator(operator_ranges, partition) == '*':
            MAX_ARITH_PARTITION_SIZE = math.ceil(
                nets_for_each_operator['*'] / len(operator_ranges['*']))
            if MAX_ARITH_PARTITION_SIZE > II:
                print("II of {} too low for * MAX_PARTITION_SIZE {}".format(II,
                      MAX_ARITH_PARTITION_SIZE))
            m.addConstr(quicksum(x[v, partition]
                        for v in range(V)) <= MAX_ARITH_PARTITION_SIZE)
        # str(partition) in arithmetic_operators and arithmetic_operators[str(partition)] == '+':# >= operator_ranges['+'][0] and partition <=  operator_ranges['+'][1]:
        elif partition_operator(operator_ranges, partition) == '+':
            MAX_ARITH_PARTITION_SIZE = math.ceil(
                nets_for_each_operator['+'] / len(operator_ranges['+']))
            if MAX_ARITH_PARTITION_SIZE > II:
                print("II of {} too low for + MAX_PARTITION_SIZE {}".format(II,
                      MAX_ARITH_PARTITION_SIZE))
            if VERBOSE:
                print("MAX_ARITH_PARTITIONS_SIZE +: {}".format(MAX_ARITH_PARTITION_SIZE))
            m.addConstr(quicksum(x[v, partition]
                        for v in range(V)) <= MAX_ARITH_PARTITION_SIZE)
        elif partition_operator(operator_ranges, partition) == 'IN' or partition_operator(operator_ranges, partition) == 'OUT':
            continue
        else:
            # import pdb; pdb.set_trace
            print('TODO this operator')
            # m.addConstr( quicksum( x[v,partition] for v in range(V) ) <= MAX_ARITH_PARTITION_SIZE )

    # FOR IO OPERATIONS
    # (3)a partition size LB
    MIN_IO_PARTITION_SIZE = 0
    for partition in range(K):
        if partition in operator_ranges['IN']:
            m.addConstr(quicksum(x[v, partition] for v in range(
                V)) >= MIN_IO_PARTITION_SIZE)  # TODO can update
        elif partition in operator_ranges['OUT']:
            m.addConstr(quicksum(x[v, partition] for v in range(
                V)) >= MIN_IO_PARTITION_SIZE)  # TODO can update
    # (3)b partition size UB
    # can't be V/K because we don't balance things out?
    MAX_IO_PARTITION_SIZE = math.ceil(
        (len(in_nodes)+len(out_nodes)) / (len(operator_ranges['IN'])+len(operator_ranges['OUT'])))
    MAX_IN_PARTITION_SIZE = math.ceil(
        len(in_nodes) / len(operator_ranges['IN']))
    MAX_OUT_PARTITION_SIZE = math.ceil(
        len(out_nodes) / len(operator_ranges['OUT']))
    # if MAX_IO_PARTITION_SIZE > II * self.C:
    #     print("II of {} too low for IO_MAX_PARTITION_SIZE {}".format( II, MAX_IO_PARTITION_SIZE))
    # MAX_IO_PARTITION_SIZE = #math.ceil( V/K) # len(arithmetic_operators) / K ) # TODO can update
    for partition in range(K):
        # if VERBOSE:
        #     print("MAX_IO_PARTITION_SIZE", MAX_IO_PARTITION_SIZE)
        # >= operator_ranges['IO'][0] and partition <=  operator_ranges['IO'][1]:
        if partition in operator_ranges['IN']:
            # MAX_IO_PARTITION_SIZE = MAX_IO_PARTITION_SIZE + 8
            m.addConstr(quicksum(x[v, partition]
                        for v in range(V)) <= MAX_IN_PARTITION_SIZE)
        # >= operator_ranges['IO'][0] and partition <=  operator_ranges['IO'][1]:
        elif partition in operator_ranges['OUT']:
            # MAX_IO_PARTITION_SIZE = MAX_IO_PARTITION_SIZE + 8
            m.addConstr(quicksum(x[v, partition]
                        for v in range(V)) <= MAX_OUT_PARTITION_SIZE)

    # "net constraints"
    for h in range(H):
        for v in range(V):
            if v in netlist[h]:
                for partition in range(K):
                    m.addConstr(y[h, partition] - x[v, partition] <= 0)

    # custom region constraints.
    for v in range(V):

        if str(v) in arithmetic_operators:
            operator_range = operator_ranges[arithmetic_operators[str(v)]]
            print(f'{arithmetic_operators[str(v)]}')
            m.addConstr(quicksum(x[v, partition]
                        for partition in operator_range) == 1)
            # don't want this partition to be anywhere else: none unconstrained
        elif str(v) in in_nodes:
            operator_range = operator_ranges['IN']
            m.addConstr(quicksum(x[v, partition]
                        for partition in operator_range) == 1)
        elif str(v) in out_nodes:
            operator_range = operator_ranges['OUT']
            m.addConstr(quicksum(x[v, partition]
                        for partition in operator_range) == 1)
        else:
            # operator_range = operator_ranges[ 'IO' ]
            # for part in range( operator_range[0], operator_range[1] + 1 ):
            #     print( "node {} must be in partition {}".format(v, part))
            # m.addConstr( quicksum( x[v,partition] for partition in range( operator_range[0], operator_range[1] + 1) ) == 1 )
            print(f'node {v} is neither an arithmetic operator nor an IO...')
    # limit crowding
    # no more than the average
    #     # if str(v) in arithmetic_operators:
    # for opr, operator_range in operator_ranges.items():
        # operator_range = operator_ranges[ arithmetic_operators[ str(v) ] ]
        # for partition in range( operator_range[0], operator_range[1] + 1 ):
    # for partition in range(K):
    #     # num_of_partitions_for_op = operator_range[1] - operator_range[0] + 1
    #         #     m.addConstr( quicksum( x[v,partition] for v in range(V) )<=  2)

    # solve
    # if fails m.computeIIS();
    t1 = timeit.default_timer()
    m.write(os.path.realpath(log_dir) + '/' + 'debug-partition.mps')
    m.write(os.path.realpath(log_dir) + '/' + 'debug-partition.lp')
    m.optimize()
    assert (m.Status == 2), "Could not find a feasible solution with these parameters"
    t2 = timeit.default_timer()
    # solFilename = 'results/' + benchmark + "-K" + K + '.sol'
    solFile = open(partition_filename, "w+")
    VERBOSE = False
    if VERBOSE:
        for h in range(H):
            for partition in range(K):
                yLine = 'y[%d][%d] = %d' % (h, partition, y[h, partition].x)
                print(yLine)
                solFile.write(yLine + '\n')
        for v in range(V):
            for partition in range(K):
                xLine = 'x[%d][%d] = %d' % (v, partition, x[v, partition].x)
                print(xLine)
                solFile.write(xLine + '\n')
    ret = [0] * (V)
    partition_operators = {}
    partition_operator_list = [-1]*K
    num_p_for_each_partition = {}
    for v in range(V):
        for partition in range(K):
            if x[v, partition].x == 1:
                ret[v] = partition
                xLine = '%d -> %d' % (v, partition)
                if VERBOSE:
                    print(xLine)
                solFile.write(xLine + '\n')
                if str(partition) not in partition_operators and str(v) in arithmetic_operators:
                    partition_operators[str(
                        partition)] = arithmetic_operators[str(v)]
                    partition_operator_list[partition] = arithmetic_operators[str(
                        v)]
                elif str(partition) not in partition_operators and str(v) in in_nodes:
                    partition_operators[str(partition)] = in_nodes[str(v)]
                    partition_operator_list[partition] = in_nodes[str(v)]
                elif str(partition) not in partition_operators and str(v) in out_nodes:
                    partition_operators[str(partition)] = out_nodes[str(v)]
                    partition_operator_list[partition] = out_nodes[str(v)]
                if partition in num_p_for_each_partition:
                    num_p_for_each_partition[partition] = num_p_for_each_partition[partition] + 1
                else:
                    num_p_for_each_partition[partition] = 1
    partition_operator_ = [0] * K
    for partition in range(K):
        partition_operator_[partition] = partition_operator(
            operator_ranges, partition)

    print("Wrote solution to {0}".format(partition_filename))
    setupTime = t1 - t0
    solveTime = t2 - t1
    ioTime = timeit.default_timer() - t2

    '''
    'ret' is which partition each node in the hypergraph is assigned to
    '''

    return ret, partition_operator_
