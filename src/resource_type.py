import enum


class ResourceType(enum.Enum):
    PE = 1
    PE_IN = 2
    PE_IN_PORT = 3
    PE_OUT = 4
    PE_OUT_PORT = 5
    H_NOC = 6
    V_NOC = 7
    SWITCH_N = 8
    SWITCH_E = 9
    PE_IN_SWITCH = 10
    PE_OUT_SWITCH = 11
