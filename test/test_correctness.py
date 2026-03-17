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
            "python3", "run_mocarabe.py",
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
    assert result.returncode == 0, f"run_mocarabe.py failed:\n{result.stdout}\n{result.stderr}"

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


def test_int_adder_chain_ii4():
    output = run_simulation("hgr/int_adder_chain", ii=4)
    assert_no_errors(output)


def test_int_poly_quadratic_ii1():
    output = run_simulation("hgr/int_poly_quadratic", ii=1, c=40)
    assert_no_errors(output)


def test_int_poly_quadratic_ii2():
    output = run_simulation("hgr/int_poly_quadratic", ii=2, c=40)
    assert_no_errors(output)


def test_int_poly_quadratic_ii3():
    output = run_simulation("hgr/int_poly_quadratic", ii=3, c=40)
    assert_no_errors(output)


# ── Known-failing benchmarks ──────────────────────────────────────────────────
# These tests document current bugs so we notice when they get fixed.
# Each uses strict=True: an unexpected pass (XPASS) will fail the suite.

# Bug: ILP scheduler produces infeasible model for larger benchmarks at C=20.
# Root cause unclear — likely the NoC routing model becomes overconstrained when
# the number of nets is large relative to C*II.

@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ILP scheduling infeasible: int_sobel has 25 nets on 2x13 torus with C=20")
def test_xfail_int_sobel_ii1():
    output = run_simulation("hgr/int_sobel", ii=1)
    assert_no_errors(output)


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ILP scheduling infeasible: int_iir8 has 51 nets, SCIP finds no solution")
def test_xfail_int_iir8_ii1():
    output = run_simulation("hgr/int_iir8", ii=1)
    assert_no_errors(output)


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ILP scheduling infeasible: int_dct has 69 nets, SCIP finds no solution")
def test_xfail_int_dct_ii1():
    output = run_simulation("hgr/int_dct", ii=1)
    assert_no_errors(output)


# Bug: pe_memory_gen port conflict — two operands are assigned the same PE input
# port in the same schedule timeslot.  Raises AssertionError in
# generate_op_addresses_and_op_port_select().  Observed when 'C' is raised to give
# the scheduler more channels but the placement still produces conflicting edges.

@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="pe_memory_gen port conflict: two operands claim the same PE port/timeslot")
def test_xfail_int_sobel_ii1_c40():
    output = run_simulation("hgr/int_sobel", ii=1, c=40)
    assert_no_errors(output)


# Bug: placer co-locates an IO node with a compute node at the same PE.
# PECONF is then set to the compute type (add/mul), so the IO PE never outputs
# the testbench-driven value — it outputs 0 or X instead, cascading failures.
# Observed in int_level1_linear where nodes x2/c2 share PEs with adders.

@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="placer bug: IO node packed with compute node; PECONF set to compute type")
def test_xfail_int_level1_linear_ii1():
    output = run_simulation("hgr/int_level1_linear", ii=1, c=40, place_time=0.5)
    assert_no_errors(output)
