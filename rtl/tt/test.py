# SPDX-FileCopyrightText: © 2026 Fred Tombs
# SPDX-License-Identifier: Apache-2.0
#
# Programs the Mocarabe array through the soft bitstream, streams random inputs
# through the shared input bus and checks every output against the kernel's DFG.
# Written by mocarabe's TinyTapeout export (python -m mocarabe.tt_export); the
# kernel lives in mocarabe_program.json and bitstream.hex.

import json
import pathlib
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge

HERE = pathlib.Path(__file__).parent
PROGRAM = json.loads((HERE / "mocarabe_program.json").read_text())
BITSTREAM = [int(word, 16) for word in (HERE / "bitstream.hex").read_text().split()]
ITERATIONS = 16


def evaluate(input_values):
    """Every DFG node's value for one iteration, wrapping at the datapath width"""
    nodes = PROGRAM["nodes"]
    mask = 2 ** PROGRAM["data_width"] - 1
    values = dict(input_values)

    def value(node):
        if node not in values:
            label = nodes[node]["label"]
            a, b = (value(operand) for operand in nodes[node]["operands"])
            if label == "+":
                values[node] = (a + b) & mask
            elif label == "*":
                values[node] = (a * b) & mask
            else:  # an output shows its operand
                values[node] = a
        return values[node]

    return {node: value(node) for node in nodes}


def iteration_inputs(rng):
    """Input values for one iteration: constants are themselves, inputs random.
    Copies of one input (split_input_fanout) get the same value."""
    mask = 2 ** PROGRAM["data_width"] - 1
    by_name = {}
    values = {}
    for i in PROGRAM["inputs"]:
        name = i["name"]
        if name not in by_name:
            by_name[name] = int(name) & mask if name.lstrip("-").isnumeric() else rng.randrange(mask + 1)
        values[i["node"]] = by_name[name]
    return values


async def program(dut):
    """Reset, stream the bitstream in, then flush the FIFOs with rst_n held low"""
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)  # cfg_en low for at least one clock resets the loader
    for word in BITSTREAM:
        await FallingEdge(dut.clk)
        dut.uio_in.value = 1  # cfg_en
        dut.ui_in.value = word
    await FallingEdge(dut.clk)
    dut.uio_in.value = 0
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, PROGRAM["flush_cycles"])


@cocotb.test()
async def test_kernel(dut):
    dut._log.info(
        f"Kernel: {len(PROGRAM['inputs'])} inputs, {len(PROGRAM['outputs'])} outputs, "
        f"II={PROGRAM['ii']}, {len(BITSTREAM)} configuration words"
    )
    clock = Clock(dut.clk, 20, unit="ns")  # 50 MHz
    cocotb.start_soon(clock.start())

    await program(dut)

    # what goes on ui_in, and what must come out of uo_out, run cycle by run cycle
    rng = random.Random(1)
    ii = PROGRAM["ii"]
    bus, expected = {}, {}
    for k in range(ITERATIONS):
        inputs = iteration_inputs(rng)
        values = evaluate(inputs)
        for i in PROGRAM["inputs"]:
            bus[i["cycle"] + k * ii] = inputs[i["node"]]
        for o in PROGRAM["outputs"]:
            expected[o["cycle"] + k * ii] = (o["label"], k, values[o["node"]])

    # rst_n rises on a falling edge, so the next rising edge is run cycle 0; inputs
    # are set before the rising edge that samples them, outputs read before it
    checked = 0
    for cycle in range(max(expected) + 1):
        await FallingEdge(dut.clk)
        dut.rst_n.value = 1
        dut.ui_in.value = bus.get(cycle, 0)
        if cycle in expected:
            label, k, value = expected[cycle]
            got = int(dut.uo_out.value)
            valid = int(dut.uio_out.value) >> 1 & 1
            assert valid == 1, f"run cycle {cycle}: io_out_valid low for {label} iteration {k}"
            assert got == value, f"run cycle {cycle}: {label} iteration {k} is {got}, expected {value}"
            checked += 1

    dut._log.info(f"{checked} outputs matched")
