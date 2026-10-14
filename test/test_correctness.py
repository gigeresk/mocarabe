# Tests to ensure that simulations are running correctly

import json
import subprocess
import re
import os
import pytest

MOCARABE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IVERILOG_CMD = (
    "iverilog -g2012 -o mocarabe_sim.vvp "
    "mocarabe.sv pe_2_input.sv torus_switch.sv pe_srl.v "
    "pe_mux_2_input.sv pe_mux_3_input.sv pe_mux_n_input.sv SRL16E.v SRLC32E.v SRL64.v mocarabe_tb.sv"
)
SIM_TIMEOUT = 60

def generate_project(
    dfg,
    ii,
    iod=1,
    ard=1,
    c=20,
    place_time=0.1,
    sched_method="ILP",
    device=None,
    max_c=None,
    split_input_fanout=False,
):
    """Run mocarabe and return the generated rtl directory.

    With device, c=None takes the channel count from the device file.  max_c
    starts at c and raises it until the ILP finds a schedule.
    """
    cmd = ["python3", "-m", "mocarabe", "-dfg", dfg, "-II", str(ii)]
    if device:
        cmd += ["--device", device]
    else:
        cmd += ["-iod", str(iod), "-ard", str(ard)]
    if c is not None:
        cmd += ["-C", str(c)]
    if max_c is not None:
        cmd += ["--max_C", str(max_c)]
    if split_input_fanout:
        cmd += ["--split_input_fanout"]
    cmd += ["--place_time", str(place_time), "--sched_method", sched_method]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=MOCARABE_ROOT)
    assert result.returncode == 0, f"mocarabe failed:\n{result.stdout}\n{result.stderr}"

    # Extract the rtl directory from the output
    match = re.search(r"cd (proj/\S+/rtl/)", result.stdout)
    assert match, f"Could not find rtl dir in mocarabe output:\n{result.stdout}"
    return os.path.join(MOCARABE_ROOT, match.group(1))


def simulate(rtl_dir):
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


def run_simulation(dfg, ii, **kwargs):
    return simulate(generate_project(dfg, ii, **kwargs))


@pytest.mark.timeout(SIM_TIMEOUT)
def assert_no_errors(sim_output):
    errors = [line for line in sim_output.splitlines() if "Assert error" in line]
    assert not errors, "Simulation assertion failures:\n" + "\n".join(errors)
    assert "=== PASS" in sim_output, "Simulation did not report PASS:\n" + sim_output[-2000:]


@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_adder_chain_ii1():
    output = run_simulation("hgr/int_adder_chain", ii=1)
    assert_no_errors(output)


@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_adder_chain_ii2():
    output = run_simulation("hgr/int_adder_chain", ii=2)
    assert_no_errors(output)


@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_adder_chain_ii3():
    output = run_simulation("hgr/int_adder_chain", ii=3)
    assert_no_errors(output)


@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_adder_chain_ii4():
    output = run_simulation("hgr/int_adder_chain", ii=4)
    assert_no_errors(output)


@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_poly_quadratic_ii1():
    output = run_simulation("hgr/int_poly_quadratic", ii=1, c=40)
    assert_no_errors(output)


@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_poly_quadratic_ii2():
    output = run_simulation("hgr/int_poly_quadratic", ii=2, c=40)
    assert_no_errors(output)


@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_poly_quadratic_ii3():
    output = run_simulation("hgr/int_poly_quadratic", ii=3, c=40)
    assert_no_errors(output)


# ── Fixed device flow ─────────────────────────────────────────────────────────
# PE types and layout come from devices/*.json instead of being sized to the DFG.


def expected_peconf(device_file):
    """PECONF hex for a device grid: one nibble per PE, pe_id = x + y*Nx, LSB first"""
    with open(os.path.join(MOCARABE_ROOT, device_file)) as f:
        rows = [row.split() for row in json.load(f)["grid"]]
    op_code = {"+": "0", "*": "1", "IO": "2"}
    pes = [op_code[t] for row in reversed(rows) for t in row]  # first row is the top
    return "".join(reversed(pes))


def run_fixed_device(dfg, ii, device):
    rtl_dir = generate_project(dfg, ii, c=None, device=device)
    with open(os.path.join(rtl_dir, "benchmark.h")) as f:
        peconf = re.search(r"`define PECONF \d+'h(\w+)", f.read()).group(1)
    assert peconf == expected_peconf(device), "PE types do not match the device file"
    assert_no_errors(simulate(rtl_dir))


@pytest.mark.timeout(SIM_TIMEOUT)
def test_fixed_device_int_adder_chain_ii2():
    run_fixed_device("hgr/int_adder_chain", 2, "devices/tt_3x3_1mul.json")


@pytest.mark.timeout(SIM_TIMEOUT)
def test_fixed_device_int_poly_quadratic_ii2():
    # both multiplies share the single '*' PE
    run_fixed_device("hgr/int_poly_quadratic", 2, "devices/tt_3x3_1mul.json")


@pytest.mark.timeout(SIM_TIMEOUT)
def test_fixed_device_4x4_int_poly_quadratic_ii2():
    run_fixed_device("hgr/int_poly_quadratic", 2, "devices/tt_4x4_1mul.json")


# ── Larger benchmarks ─────────────────────────────────────────────────────────
# The scheduling ILP grows with C, so large C runs out of solver time rather than
# being infeasible.  These start at low C and let the scheduler raise it.


@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_sobel_ii1():
    # fanout-4 nets; needs cycle-free routing and FIFO-bounded operand timing
    output = run_simulation("hgr/int_sobel", ii=1, c=2, max_c=8)
    assert_no_errors(output)


@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_iir8_ii1():
    # outputs y0..y6 also feed later stages; values overflow 32 bits
    output = run_simulation("hgr/int_iir8", ii=1, c=2, max_c=8)
    assert_no_errors(output)


@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_level1_linear_ii1():
    output = run_simulation("hgr/int_level1_linear", ii=1, c=2, max_c=8)
    assert_no_errors(output)


@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_approx1_ii1():
    # T2*T2: one net feeds both ports of the same PE
    output = run_simulation("hgr/int_approx1", ii=1, c=2, max_c=8)
    assert_no_errors(output)


@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_poly4_ii1_split_input_fanout():
    # Horner form: x feeds every stage, so one x would wait longer than the
    # 64-deep FIFOs allow; each consumer gets its own copy of x instead
    output = run_simulation(
        "hgr/int_poly4", ii=1, c=2, max_c=8, split_input_fanout=True
    )
    assert_no_errors(output)
