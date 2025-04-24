import math

import numpy as np

from src.device import Device
from .base import PEAllocatorStrategy

class ClosestFactorsAllocator( PEAllocatorStrategy ):    
    #TODO get rid of/make II-relative (again) io_diffusion and arith_diffusion
    def allocate_pes( self, dataflow_hgraph, II, io_diffusion, arith_diffusion ):
        """
        Allocates an Nx x Ny array with consideration for the DFG
         (dataflow_hgraph) and the II, but without resource constraints.  Array
         shape is determined using the closest two factors of the system size

        Parameters
        ----------
        dataflow_hgraph : DataflowHypergraph DFG to extract operators (including
            I/O)

        II : int Initiation interval/context count.  Determines how many DFG
            nodes get mapped to one PE  

        io_diffusion : float
            More info to be displayed (default is None)

        arith_diffusion : float
            More info to be displayed (default is None)

        Returns
        -------
        int, int, np.ndarray
        """

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
            num_partitions_given_to_operator[op] = math.ceil( count / (arith_diffusion) )

        # how many of each IO operator?

        num_partitions_given_to_operator['OUT'] = math.ceil( len(node_out) / (io_diffusion) )
        num_partitions_given_to_operator['IN'] = math.ceil( len(node_in) / (io_diffusion) )

        system_size = sum( num_partitions_given_to_operator.values() )

        while self._is_prime( system_size ):
            system_size = system_size + 1
            num_partitions_given_to_operator['IN'] = num_partitions_given_to_operator['IN'] + 1

        # closest factors
        Nx, Ny = self._closest_factors( system_size )

        device_map = np.ndarray( (Nx, Ny), dtype=object )

        count = 0
        for operation, num in num_partitions_given_to_operator.items():
            for i in range(num): 
                device_map[count % Nx][count // Nx] = operation
                count += 1  
        
        return Nx, Ny, device_map

