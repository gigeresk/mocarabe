import math
import sys

import numpy as np

from .base import PEAllocatorStrategy


def logical_to_physical(logical_x, logical_y, Nx, Ny):
    # I don't have a closed form so I just invert physical_to_logical

    for x in range(Nx):
        for y in range(Ny):
            this_logical_x, this_logical_y = [*physical_to_logical(x, y, Nx, Ny)]
            if (this_logical_x, this_logical_y) == (logical_x, logical_y):
                return (x, y)


def physical_to_logical(physical_x, physical_y, Nx, Ny):

    logical_x = physical_x
    if physical_x % 2 == 1:  # odd
        logical_x = Nx - int((physical_x + 1) / 2)
    else:  # even
        logical_x = physical_x // 2

    logical_y = physical_y
    if physical_y % 2 == 1:  # odd
        logical_y = Ny - int((physical_y + 1) / 2)
    else:  # even
        logical_y = physical_y // 2

    return (logical_x, logical_y)


class ConstrainedClosestFactorsAllocator(PEAllocatorStrategy):
    def allocate_pes(
        self,
        dataflow_hgraph,
        II,
        io_diffusion,
        arith_diffusion,
        device_constraints,
        separate_i_and_o=True,
    ):
        # We need DSPs for multipliers, so we constrain our system sizes around these
        # No other operator type needs this

        device_operator_allocation = (
            PEAllocatorStrategy._paint_device_with_op_constraints(device_constraints)
        )

        for x in range(PEAllocatorStrategy.MAX_DEVICE_X_DIM - 1, -1, -1):
            for y in range(PEAllocatorStrategy.MAX_DEVICE_Y_DIM):
                a = device_operator_allocation[x][y]
                if a == None:
                    sys.stdout.write("_")
                else:
                    sys.stdout.write(str(a))
                sys.stdout.write(" ")
            sys.stdout.write("\n")
        # Allocate PEs to each operator type

        # how much we want every io or arith PE to be utilized (on avg)
        # io_diffusion = min( io_diffusion, 1.0 )
        # arith_diffusion = min( arith_diffusion, 1.0 )

        # node_labels = dataflow_hgraph.extract_labels()

        node_operators = dataflow_hgraph.extract_node_arithmetic_operators()
        node_in = dataflow_hgraph.extract_input_nodes()
        node_out = dataflow_hgraph.extract_output_nodes()
        operator_count = {}

        for operator_label in node_operators.values():
            if operator_label not in operator_count:
                operator_count[operator_label] = 1
            else:
                operator_count[operator_label] += 1

        # how many of each non-IO operator do we need?

        num_partitions_given_to_operator = {}
        for op, count in operator_count.items():
            num_partitions_given_to_operator
            num_partitions_given_to_operator[op] = math.ceil(count / (arith_diffusion))

        # how many of each IO operator?

        num_partitions_given_to_operator["OUT"] = math.ceil(
            len(node_out) / (io_diffusion)
        )
        num_partitions_given_to_operator["IN"] = math.ceil(
            len(node_in) / (io_diffusion)
        )

        # for operator, num_partitions in num_partitions_given_to_operator.items():
        #     # From (0,0) out, we try to find the minimum num of operators to satisfy our constraints
        #     # (0,0) -> (0,1),(1,1),(1,0) -> ()
        #     for
        num_multipliers = 0
        current_Nx = 0
        current_Ny = 0
        # num_all_other_types = sum(num_partitions_given_to_operator.values()) - num_partitions_given_to_operator['*']

        x_jump = 2
        y_jump = 1

        for bbox_size in range(0, PEAllocatorStrategy.MAX_DEVICE_X_DIM, x_jump):
            current_Nx = bbox_size
            current_Ny = bbox_size

            num_multipliers = 0
            for scan_x in range(0, bbox_size, x_jump):
                for scan_y in range(0, bbox_size, y_jump):
                    current_Nx = scan_x
                    current_Ny = scan_y
                    if device_operator_allocation[scan_x][scan_y] == "*":
                        # print(f'tro {num_multipliers}')
                        num_multipliers += 1
            if "*" in num_partitions_given_to_operator:
                if num_multipliers >= num_partitions_given_to_operator["*"]:
                    break

        print(f"Nx={current_Nx}, Ny={current_Ny}")

        system_size = sum(num_partitions_given_to_operator.values())

        while self._is_prime(system_size):
            system_size = system_size + 1
            num_partitions_given_to_operator["IN"] = (
                num_partitions_given_to_operator["IN"] + 1
            )

        # closest factors
        Nx, Ny = self._closest_factors(system_size)

        # delete
        for x in range(PEAllocatorStrategy.MAX_DEVICE_X_DIM - 1, Nx - 1, -1):
            device_operator_allocation = np.delete(
                device_operator_allocation, (x), axis=0
            )
        for y in range(PEAllocatorStrategy.MAX_DEVICE_Y_DIM - 1, Ny - 1, -1):
            device_operator_allocation = np.delete(
                device_operator_allocation, (y), axis=1
            )

        for op, count in operator_count.items():
            print(
                f"{op} has {num_partitions_given_to_operator[op]} PEs and {count} operations.\
            Effective diffusion: {count / num_partitions_given_to_operator[op]}"
            )

        return Nx, Ny, device_operator_allocation
