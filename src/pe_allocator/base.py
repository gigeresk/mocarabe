import abc
import math

import numpy as np

class PEAllocatorStrategy(metaclass=abc.ABCMeta):

    MAX_DEVICE_X_DIM = 20
    MAX_DEVICE_Y_DIM = 19

    @abc.abstractmethod
    def allocate_pes( self ):
        pass

    @staticmethod
    def _closest_factors( n ):
        assert( n > 0 ), 'System size must be greater than 0'

        test_num = int( math.sqrt( n ) )
        while (n % test_num ) != 0:
            test_num = test_num - 1

        x = test_num
        y = n / test_num
        assert( x == int( x ) )
        assert( y == int( y ) )
        x = int(x)
        y = int(y)

        return x, y

    @staticmethod
    def _is_prime(n):
        if n == 2 or n == 3: return True
        if n < 2 or n%2 == 0: return False
        if n < 9: return True
        if n%3 == 0: return False
        r = int(n**0.5)
        # since all primes > 3 are of the form 6n ± 1
        # start with f=5 (which is prime)
        # and test f, f+2 for being prime
        # then loop by 6.
        f = 5
        while f <= r:
            print('\t',f)
            if n % f == 0: return False
            if n % (f+2) == 0: return False
            f += 6
        return True

    @staticmethod
    def _paint_device_with_op_constraints( device_constraints ):
        device_operator_allocation = np.ndarray( (PEAllocatorStrategy.MAX_DEVICE_X_DIM, PEAllocatorStrategy.MAX_DEVICE_Y_DIM), dtype=object )#[[ '' for y in range(MAX_DEVICE_Y_DIM)] for x in range(MAX_DEVICE_X_DIM)]

        for constraint in device_constraints:
            if device_constraints == '': continue
            # e.g. (x,y) '*'
            constr_x = constraint[0][0]
            constr_y = constraint[0][1]
            constraint_op = constraint[1]

            if constr_x != '-' and constr_y != '-':
                # Applies to specific cell
                device_operator_allocation[constr_x][constr_y] = constraint_op
            elif constr_y == '-':
                # Applies to entire column
                for y in range(PEAllocatorStrategy.MAX_DEVICE_Y_DIM):
                    device_operator_allocation[constr_x][y] = constraint_op
            elif constr_x == '-':
                # Applies to entire row
                for x in range(PEAllocatorStrategy.MAX_DEVICE_X_DIM):
                    device_operator_allocation[x][constr_y] = constraint_op
            else:
                # Applies to entire array
                for x in range(PEAllocatorStrategy.MAX_DEVICE_X_DIM):
                    for y in range(PEAllocatorStrategy.MAX_DEVICE_Y_DIM):
                        device_operator_allocation[x][y] = constraint_op

        return device_operator_allocation