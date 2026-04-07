import sys
import math
# print("\n\n\nTODO delete operator_map/__init__.py\n\n\n")


class DeviceMap:
    # from ._operator_allocator import operator_allocator_with_constraints
    def __init__(self, dataflow_hgraph, II, io_diffusion, arith_diffusion):
        # from ._operator_allocator import auto_operator_allocator

        self.II = II
        self.num_partitions_given_to_operator = 1
        self.Nx = self.Ny = 1
        # self.num_partitions_given_to_operator, self.Nx, self.Ny = auto_operator_allocator( dataflow_hgraph, II, io_diffusion, arith_diffusion )

    def __str__(self):
        string = "\nOperation Allocation (unpartitioned and unplaced)\n"
        operator_assortment = [0] * self.Nx * self.Ny
        operator_count = 0
        for operator, num_partitions in self.num_partitions_given_to_operator.items():
            for num in range(0, num_partitions):
                operator_assortment[operator_count + num] = operator
            operator_count = operator_count + num_partitions
        for y in range(self.Ny - 1, -1, -1):
            string = string + "+" + self.Nx * "-----+" + "\n"
            for x in range(0, self.Nx):
                string = string + "|"
                id_ = y * self.Nx + x
                operator_str = str(operator_assortment[id_])
                padding = 5 - len(operator_str)
                padding = max(padding, 0)
                left_padding = padding - (padding // 2)
                right_padding = padding - left_padding

                operator_str = " " * left_padding + operator_str + " " * right_padding

                string = string + operator_str
            string = string + "|"
            string = string + "\n"

        string = string + "+" + self.Nx * "-----+" + "\n\n"
        return string


# class PartitionedOperatorMap( DeviceMap ):
#     def __init__( self, operator_map,II, Nx, Ny,num_partitions_given_to_operator,  dataflow_hgraph, partition_filename ):
#         print('initialize parititonedOperatormap')

#         self.II = II
#         self.num_partitions_given_to_operator = num_partitions_given_to_operator
#         self.Nx = Nx
#         self.Ny = Ny

#         from ._partition import partition
#         self.dfg_v_to_partition_id, self.partition_operators = partition( dataflow_hgraph, self.Nx*self.Ny, self.num_partitions_given_to_operator, partition_filename, self.II )

#     def __str__( self ):
#         string_repr = '\nPartitioning (operators allocated but not placed)\n'
#         # TODO
#         # going under the assumption that partitioning = placement
#         not_a_block_operator = [] # TODO get this to zero
#         for y in range( self.Ny-1, 0-1, -1 ):
#             string_repr = string_repr + '+' + self.Nx*'-----+' + '\n'
#             for x in range( 0, self.Nx ):
#                 string_repr = string_repr + '|'

#                 operator = self.partition_operators[ y*self.Nx + x ]
#                 # if type(operator) == int:

#                 if operator == -1:
#                     operator = '    '
#                 elif operator.isnumeric() or operator.isidentifier():#
#                     operator = ' ' + 'IO' + '  '
#                 else:
#                     operator = '  ' + str(operator) + '  '
#                 string_repr = string_repr + str(operator)
#             string_repr = string_repr + '|'
#             string_repr = string_repr + '\n'
#             for x in range( 0, self.Nx ):
#                 string_repr = string_repr +'|'
#                 num_ops_in_this_pe = str( self.num_op_for_partitions(self.dfg_v_to_partition_id )[ y*self.Nx + x] )

#                 string_repr = string_repr + ' (' + num_ops_in_this_pe + ') '

#             string_repr = string_repr + '|\n'

#         string_repr = string_repr + '+' + self.Nx*'-----+' + '\n'

#         for notblock in not_a_block_operator:
#             string_repr = string_repr +  'PE {notblock} at ({str( notblock % self.Nx )},{ str( notblock // self.Ny )}) unused!\n'

#         # prettyPrintText( '' )
#         return string_repr


#     def num_op_for_partitions( self, dfg_v_to_partition_id ):
#         from collections import Counter
#         num_op_for_each_partition = [0]*self.Nx*self.Ny

#         op_occurence_cnt = Counter( dfg_v_to_partition_id )

#         for partition_id, occurence_cnt in op_occurence_cnt.items():
#             num_op_for_each_partition[partition_id] = occurence_cnt

#         return num_op_for_each_partition

# from ._partition import partition

# class PlacedOperatorMap( PartitionedOperatorMap ):

#     def __init__( self, partitioned_op_map, dataflow_hgraph, time ):
#         self.II = partitioned_op_map.II
#         self.num_partitions_given_to_operator = partitioned_op_map.num_partitions_given_to_operator
#         self.Nx = partitioned_op_map.Nx
#         self.Ny = partitioned_op_map.Ny

#         self.partition_operators = partitioned_op_map.partition_operators
#         self.dfg_v_to_partition_id = partitioned_op_map.dfg_v_to_partition_id


#         from ._placement import placement, annealing_placement, dummy_ilp_placement
#         self.partition_to_pe_id = self.placement_result= placement( dataflow_hgraph, partitioned_op_map, '', time )

#         # self.dfg_v_to_partition_id, self.partition_operators = partition( dataflow_hgraph, self.Nx*self.Ny, self.num_partitions_given_to_operator, partition_filename, self.II )

#     # from ._placement import placement, annealing_placement, dummy_ilp_placement

#     def __str__( self ):

#         # def prettyPrintPlacedOperators( self, partition_operators, num_op_for_partitions, partition_to_pe_id, Nx, Ny ):
#         # string_repr = string_repr + ioskip )
#         string_repr =  'OPERATOR PARTITIONS (PLACED)\n\n'
#         # TODO
#         # going under the assumption that partitioning = placement
#         partition_to_pe_id= self.partition_to_pe_id
#         pe_to_partition_id = [-1] * len( partition_to_pe_id )
#         for partition, pe_id in enumerate( partition_to_pe_id ):
#             pe_to_partition_id[pe_id] = partition

#         Nx = self.Nx
#         Ny = self.Ny

#         num_op_for_partitions = self.num_op_for_partitions( self.dfg_v_to_partition_id )
#         not_a_block_operator = [] # TODO get this to zero
#         for y in range( Ny-1, 0-1, -1 ):
#             string_repr = string_repr + '+' + Nx*'-----+' + '\n'
#             for x in range( 0, Nx ):
#                 string_repr = string_repr + '|'

#                 pe_id = y*Nx + x
#                 operator = self.partition_operators[ pe_to_partition_id[ pe_id ] ]

#                 if 'IO' in str(operator):
#                     operator = ' ' + 'IO' + '  '
#                 else:
#                     operator = '  ' + str(operator) + '  '
#                 string_repr = string_repr + operator

#             string_repr = string_repr + '|\n'
#             for x in range( 0, Nx ):
#                 string_repr = string_repr + '|'

#                 pe_id = y*Nx + x
#                 partition = pe_to_partition_id[pe_id]

#                 num_ops_in_this_pe = str( num_op_for_partitions[ partition ] )

#                 string_repr = string_repr + ' (' + num_ops_in_this_pe + ') '
#             string_repr = string_repr + '|\n'

#         string_repr = string_repr + '+' + self.Nx*'-----+' + '\n'

#         # for notblock in not_a_block_operator:
#         #     string_repr = string_repr + f'PE '+str(notblock)+' at ('str( notblock % self.Nx )+', ''+ str( notblock // self.Ny )+') unused!\n'
#         return string_repr
