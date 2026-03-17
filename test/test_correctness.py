# Tests to ensure that simulations are running correctly

import subprocess
import re
import os
import pytest

MOCARABE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IVERILOG_CMD = (
    "iverilog -g2012 -o mocarabe_sim.vvp "
    "mocarabe.sv pe_2_input.sv torus_switch.sv pe_srl.v "
    "pe_mux_2_input.sv pe_mux_3_input.sv SRL16E.v SRLC32E.v SRL64.v mocarabe_tb.sv"
)


def run_simulation(dfg, ii, iod=1, ard=1, c=20, place_time=0.1, sched_method="ILP"):
    # Run mocarabe to generate the project
    result = subprocess.run(
        [
            "python3", "mocarabe.py",
            "-dfg", dfg,
            "-iod", str(iod),
            "-ard", str(ard),
            "-II", str(ii),
            "-C", str(c),
            "--place_time", str(place_time),
            "--sched_method", sched_method,
        ],
        capture_output=True, text=True, cwd=MOCARABE_ROOT
    )
    assert result.returncode == 0, f"mocarabe.py failed:\n{result.stdout}\n{result.stderr}"

    # Extract the rtl directory from the output
    match = re.search(r"cd (proj/\S+/rtl/)", result.stdout)
    assert match, f"Could not find rtl dir in mocarabe output:\n{result.stdout}"
    rtl_dir = os.path.join(MOCARABE_ROOT, match.group(1))

    # Compile
    result = subprocess.run(
        IVERILOG_CMD, shell=True, capture_output=True, text=True, cwd=rtl_dir
    )
    assert result.returncode == 0, f"iverilog failed:\n{result.stderr}"

    # Simulate
    result = subprocess.run(
        ["vvp", "mocarabe_sim.vvp"], capture_output=True, text=True, cwd=rtl_dir
    )
    return result.stdout + result.stderr


def assert_no_errors(sim_output):
    errors = [line for line in sim_output.splitlines() if "Assert error" in line]
    assert not errors, "Simulation assertion failures:\n" + "\n".join(errors)


def test_int_adder_chain_ii1():
    output = run_simulation("hgr/int_adder_chain", ii=1)
    assert_no_errors(output)


def test_int_adder_chain_ii2():
    output = run_simulation("hgr/int_adder_chain", ii=2)
    assert_no_errors(output)


def test_int_adder_chain_ii3():
    output = run_simulation("hgr/int_adder_chain", ii=3)
    assert_no_errors(output)
