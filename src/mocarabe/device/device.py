from dataclasses import dataclass, field


@dataclass
class Device:
    """Container for device configuration"""

    Nx: int
    Ny: int
    physical_channels: int
    T: int
    schedule_length: int  # make this T
    IO_I: int
    IO_O: int
    layout: int
    pe_pipelining_stages: int
    noc_pipelining_stages: int
    unroll_factor: int
    P: int
    II: int
    data_width: int = 32  # PE datapath bits; values wrap at this width
    fifo_depth: int = 64  # PE operand SRL FIFO depth; an operand waits at most fifo_depth-1
    # shared IO: every IO PE reads one input bus, so inputs (and outputs, on io_out)
    # each need their own slot; the testbench drives one stream for all IO PEs
    shared_io: bool = False
    # groups of (x, y, net) whose NoC enters ("enter") or exits ("exit")
    # must all fall in different slots, because they share one input or output port
    shared_io_groups: list = field(default_factory=list)
