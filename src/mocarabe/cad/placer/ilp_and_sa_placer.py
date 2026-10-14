import random

from .base import PlacerStrategy

from .partitioner import partition_with_ilp_scip
from .sa_placers import initialize_state, topographical_swap, debug_energy
from .sa_placers import initialize_fixed_state, same_type_partition_groups
from .sa_placers import (
    AnnealingCongestionAwarePlacer,
)


class IlpAndSimulatedAnnealingPlacer(PlacerStrategy):
    # Use ILP partitioning
    def place(
        self,
        dataflow_hypergraph,
        K,
        num_partitions_given_to_operator,
        partition_filename,
        II,
        time,
        Nx,
        Ny,
        log_dir=".",
        placement_constraints="",
        seed=0,
        fixed_device_map=None,
    ):
        # fixed_device_map: (Nx, Ny) PE types of a fixed device; partitions are
        # placed only on PEs of their own type.  None sizes PE types to the DFG.
        fixed_device = fixed_device_map is not None

        dfg_v_to_partition_id, partitioned_op_map = partition_with_ilp_scip(
            dataflow_hypergraph,
            K,
            num_partitions_given_to_operator,
            partition_filename,
            II,
            log_dir,
            seed=seed,
            fixed_device=fixed_device,
        )

        print("\n--------------Placement--------------\n")

        assert placement_constraints == "", (
            "Have not yet fully implemented placement constraints."
        )

        if fixed_device:
            initial_state = initialize_fixed_state(
                partitioned_op_map, fixed_device_map, Nx, Ny
            )
            same_type_groups = same_type_partition_groups(partitioned_op_map)
        else:
            initial_state = initialize_state(dfg_v_to_partition_id, Nx, Ny)
            same_type_groups = None

        print(
            f"Initial energy: {debug_energy(dataflow_hypergraph, partitioned_op_map, dfg_v_to_partition_id, initial_state, Nx, Ny)} "
        )

        initial_state = topographical_swap(
            dataflow_hypergraph,
            partitioned_op_map,
            dfg_v_to_partition_id,
            Nx,
            Ny,
            initial_state,
            same_type_only=fixed_device,
        )

        # placer = QuadraticWirelengthAnnealingPlacer( initial_state, dataflow_hypergraph, partitioned_op_map,Nx,Ny,dfg_v_to_partition_id)#, "svg/")
        placer = AnnealingCongestionAwarePlacer(
            initial_state,
            dataflow_hypergraph,
            partitioned_op_map,
            Nx,
            Ny,
            dfg_v_to_partition_id,
            same_type_groups=same_type_groups,
        )  # , "svg/")

        print(f"Starting energy: {placer.energy()}")

        # auto() mutates self.state during its timing loop, so save state first.
        # Restore it and re-seed before anneal() so both the starting state and
        # the random sequence are deterministic regardless of system load.
        state_snapshot = initial_state[:]
        placer.set_schedule(placer.auto(minutes=time))
        placer.state = state_snapshot
        placer.copy_strategy = "slice"
        random.seed(seed)
        partition_to_pe_id, total_wirelength = placer.anneal()

        print(f"state: {partition_to_pe_id}, final wirelength: {total_wirelength}")

        dfg_node_to_pe_xy_map = {}
        for node, partition_id in enumerate(dfg_v_to_partition_id):
            pe_id = partition_to_pe_id[partition_id]
            dfg_node_to_pe_xy_map[str(node)] = (pe_id % Nx, pe_id // Nx)

        print(
            f"Energy after annealing: {debug_energy(dataflow_hypergraph, partitioned_op_map, dfg_v_to_partition_id, partition_to_pe_id, Nx, Ny)} "
        )

        # pe operators
        pe_operators = [0] * Nx * Ny
        for partition_id, pe_id in enumerate(partition_to_pe_id):
            pe_operators[pe_id] = partitioned_op_map[partition_id]

        return dfg_node_to_pe_xy_map, pe_operators
