from dataclasses import dataclass


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
