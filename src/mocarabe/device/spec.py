"""Fixed device descriptions for the fixed-device flow.

A device file is JSON with an ASCII grid of PE types, drawn the way
pe_allocator.to_string() prints it (first row is the highest y):

    {
      "name": "tt_3x3_1mul",
      "grid": ["IO  +  IO",
               "+   *  + ",
               "IO  +  + "],
      "channels": 2
    }
"""

import json
import math
from dataclasses import dataclass

import numpy as np

PE_TYPES = ("+", "*", "IO")
# only channels 0 and 1 reach the PE through pe_mux_2_input
MIN_CHANNELS = 2


@dataclass
class DeviceSpec:
    name: str
    Nx: int
    Ny: int
    device_map: np.ndarray  # (Nx, Ny) of PE types, indexed like the allocator's device_map
    channels: int


def parse_device_spec(data, source="<device>"):
    grid = data.get("grid")
    if not grid or not isinstance(grid, list):
        raise ValueError(f"{source}: 'grid' must be a non-empty list of row strings")

    rows = [row.split() for row in grid]
    Nx, Ny = len(rows[0]), len(rows)
    for i, row in enumerate(rows):
        if len(row) != Nx:
            raise ValueError(
                f"{source}: grid row {i} has {len(row)} cells, expected {Nx}"
            )
        for token in row:
            if token not in PE_TYPES:
                raise ValueError(
                    f"{source}: unknown PE type '{token}' in grid row {i}, "
                    f"expected one of {', '.join(PE_TYPES)}"
                )

    channels = data.get("channels", MIN_CHANNELS)
    if not isinstance(channels, int) or channels < MIN_CHANNELS:
        raise ValueError(f"{source}: 'channels' must be an integer >= {MIN_CHANNELS}")

    device_map = np.ndarray((Nx, Ny), dtype=object)
    for i, row in enumerate(rows):
        y = Ny - 1 - i  # first row is the top of the array
        for x, token in enumerate(row):
            device_map[x][y] = token

    return DeviceSpec(data.get("name", source), Nx, Ny, device_map, channels)


def load_device_spec(path):
    with open(path) as f:
        return parse_device_spec(json.load(f), source=path)


def dfg_node_counts(dataflow_hgraph):
    """Number of DFG nodes that need each PE type"""
    counts = {pe_type: 0 for pe_type in PE_TYPES}
    for op in dataflow_hgraph.extract_node_arithmetic_operators().values():
        counts[op] = counts.get(op, 0) + 1
    io_nodes = set(dataflow_hgraph.extract_input_nodes()) | set(
        dataflow_hgraph.extract_output_nodes()
    )
    counts["IO"] = len(io_nodes)
    return counts


def check_dfg_fits(spec, dataflow_hgraph, II):
    """Raise ValueError if the DFG cannot fit the device at this II.

    Each PE runs at most II DFG nodes per modulo schedule.
    """
    cells = {pe_type: int(np.count_nonzero(spec.device_map == pe_type)) for pe_type in PE_TYPES}
    problems = []
    for pe_type, needed in dfg_node_counts(dataflow_hgraph).items():
        if needed == 0:
            continue
        if pe_type not in cells:
            problems.append(f"DFG has {needed} '{pe_type}' nodes but devices have no such PE type")
        elif cells[pe_type] == 0:
            problems.append(f"DFG has {needed} '{pe_type}' nodes but {spec.name} has no '{pe_type}' PEs")
        elif needed > cells[pe_type] * II:
            min_ii = math.ceil(needed / cells[pe_type])
            problems.append(
                f"{needed} '{pe_type}' nodes need II >= {min_ii} on {cells[pe_type]} "
                f"'{pe_type}' PE(s) (II={II})"
            )
    if problems:
        raise ValueError(f"DFG does not fit device {spec.name}: " + "; ".join(problems))
