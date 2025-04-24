class Device:
    def __init__( self, Nx, Ny, C, T, IO_I, IO_O, layout,pe_pipelining_stages, noc_pipelining_stages, unroll, P, II ):
        self.Nx = Nx
        self.Ny = Ny
        self.physical_channels = C
        self.T = T
        self.schedule_length = T
        self.IO_I = IO_I
        self.IO_O = IO_O
        self.layout = layout
        self.pe_pipelining_stages = pe_pipelining_stages
        self.noc_pipelining_stages = noc_pipelining_stages
        self.unroll_factor = unroll
        self.P = P
        self.II = II


    # def io_pes( self ):

# should rename away from device to "array config" or something...

