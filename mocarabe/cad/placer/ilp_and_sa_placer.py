from .base import PlacerStrategy

from .partitioner import partition_with_ilp_scip
from .sa_placers import initialize_state, topographical_swap, debug_energy
from .sa_placers import QuadraticWirelengthAnnealingPlacer, LinearWirelengthAnnealingPlacer, AnnealingCongestionAwarePlacer, BoundingBoxPlacer


class IlpAndSimulatedAnnealingPlacer(PlacerStrategy):
    # Use ILP partitioning
    def place(self, dataflow_hypergraph, K, num_partitions_given_to_operator, partition_filename, II, time, Nx, Ny, log_dir='.', placement_constraints=""):

        dfg_v_to_partition_id, partitioned_op_map = partition_with_ilp_scip(
            dataflow_hypergraph, K, num_partitions_given_to_operator, partition_filename, II, log_dir)

        print('\n--------------Placement--------------\n')

        assert (placement_constraints ==
                ''), "Have not yet fully implemented placement constraints."

        initial_state = initialize_state(dfg_v_to_partition_id, Nx, Ny)

        print(
            f"Initial energy: {debug_energy(dataflow_hypergraph, partitioned_op_map, dfg_v_to_partition_id, initial_state,  Nx, Ny)} ")

        initial_state = topographical_swap(
            dataflow_hypergraph, partitioned_op_map, dfg_v_to_partition_id, Nx, Ny, initial_state)

        # placer = QuadraticWirelengthAnnealingPlacer( initial_state, dataflow_hypergraph, partitioned_op_map,Nx,Ny,dfg_v_to_partition_id)#, "svg/")
        placer = AnnealingCongestionAwarePlacer(
            initial_state, dataflow_hypergraph, partitioned_op_map, Nx, Ny, dfg_v_to_partition_id)  # , "svg/")

        print(f'Starting energy: {placer.energy()}')

        placer.set_schedule(placer.auto(minutes=time))
        placer.copy_strategy = "slice"

        partition_to_pe_id, total_wirelength = placer.anneal()

        print(
            f'state: {partition_to_pe_id}, final wirelength: {total_wirelength}')

        dfg_node_to_pe_xy_map = {}
        for node, partition_id in enumerate(dfg_v_to_partition_id):
            pe_id = partition_to_pe_id[partition_id]
            dfg_node_to_pe_xy_map[str(node)] = (pe_id % Nx, pe_id // Nx)

        print(
            f"Energy after annealing: {debug_energy(dataflow_hypergraph, partitioned_op_map, dfg_v_to_partition_id, partition_to_pe_id, Nx, Ny)} ")

        # pe operators
        pe_operators = [0] * Nx * Ny
        for partition_id, pe_id in enumerate(partition_to_pe_id):
            pe_operators[pe_id] = partitioned_op_map[partition_id]

        return dfg_node_to_pe_xy_map, pe_operators
