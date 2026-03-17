from .base import PlacerStrategy


class SimulatedAnnealingPlacer(PlacerStrategy):
    ''' Experimental: use SA to place operator types using device constraints, then use SA to place dfg nodes onto appropriate PEs'''

    def place(self, dataflow_hypergraph, K, num_partitions_given_to_operator, partition_filename, II, time, Nx, Ny, log_dir='.', placement_constraints=""):

        initial_state, mul_nodes, add_nodes, io_nodes = initialize_state_ok(
            Nx, Ny, II, dataflow_hypergraph, num_partitions_given_to_operator)

        cluster = AnnealingClusterPlacer(
            initial_state, II, dataflow_hypergraph, Nx, Ny, mul_nodes, add_nodes, io_nodes)
        print('initial wirelength:'+str(cluster.energy())+'\n\n\n')
        cluster.set_schedule(cluster.auto(minutes=time))
        cluster.copy_strategy = "slice"
        cluster_result, total_wirelength = cluster.anneal()

        placer = AnnealingNotSurePlacer(
            cluster_result, dataflow_hypergraph, Nx, Ny, II, mul_nodes, add_nodes, io_nodes)

        placer.set_schedule(placer.auto(minutes=time))
        placer.copy_strategy = "slice"
        placer.energy()
        dfg_to_pe_id, total_wirelength = placer.anneal()
        print('final wirelength: '+str(total_wirelength))

        dfg_node_to_pe_xy_map = {}
        for node, pe_id in enumerate(dfg_to_pe_id):
            dfg_node_to_pe_xy_map[node] = (pe_id % Nx, pe_id // Nx)

        return dfg_node_to_pe_xy_map
