from .closest_factors import ClosestFactorsAllocator
from .constrained_closest_factors import ConstrainedClosestFactorsAllocator


def allocate_pe_with_strategy( dataflow_hgraph, II, io_diffusion, arith_diffusion, device_constraints=[], strategy="closest_factors" ):
    ''' Call the specified PE allocation strategy '''

    if strategy in ["closest_factors", [], None]:
        return ClosestFactorsAllocator().allocate_pes( dataflow_hgraph, II, io_diffusion, arith_diffusion )
    elif strategy == "constrained_closest_factors":
        return ConstrainedClosestFactorsAllocator().allocate_pes( dataflow_hgraph, II, io_diffusion, arith_diffusion, device_constraints )
    else:
        raise ValueError(f"strategy must have a valid value, not {strategy} of type {type(strategy)}")

def to_string( device_map ):
    '''
    Returns a string to visualize an allocated PE array.  Run on the output of 
        an allocation strategy

    Parameters:
        device_map (np.ndarray): A decimal integer

    Returns:
            binary_sum (str): Binary string of the sum of a and b
    
    

    II : int Initiation interval/context count.  
    Determines how many DFG
        nodes get mapped to one PE  

    io_diffusion : float
        More info to be displayed (default is None)

    arith_diffusion : float
        More info to be displayed (default is None)

    Returns
    -------
    str
    '''
    string = f'PEs allocated but unplaced, {device_map.shape[0]}x{device_map.shape[1]} array\n'
    for y in range( device_map.shape[1]-1, -1, -1 ):
        string = string + '+' + device_map.shape[0]*'-----+' + '\n'
        for x in range( device_map.shape[0] ):
            string = string + '|'
            operator_str = str(device_map[x][y])
            padding = 5 - len( operator_str )
            padding = max( padding, 0 )
            left_padding = padding - (padding // 2)
            right_padding = padding - left_padding
            operator_str = ' '*left_padding + operator_str + ' '*right_padding
            string = string +  operator_str
        string = string + '|'
        string = string +  '\n'

    string = string + '+' + device_map.shape[0]*'-----+' + '\n\n'
    return string
