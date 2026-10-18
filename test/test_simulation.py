# Generate projects, simulate them with iverilog, and check the testbench assertions.
#
# Every generated project carries both bitstreams: the hard one ($readmem of the
# .dat files) and the soft one (bitstream.hex, programmed serially before the run).
# simulate() picks one at compile time with -DBITSTREAM_SOFT, so tests cover hard
# mode, soft mode, and the two agreeing cycle by cycle on the same project.

import json
import shutil
import subprocess
import re
import os

import pytest

from mocarabe.rtl_gen.bitstream_gen import read_frames

MOCARABE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RTL_FILES = (
    "mocarabe.sv pe_2_input.sv torus_switch.sv pe_srl.v "
    "pe_mux_2_input.sv pe_mux_3_input.sv pe_mux_n_input.sv "
    "cfg_loader.sv cfg_row.sv pe_cfg.sv "
    "SRL16E.v SRLC32E.v SRL64.v mocarabe_tb.sv"
)
SIM_TIMEOUT = 60

HARD = pytest.mark.parametrize("mode", ["hard"])
SOFT = pytest.mark.parametrize("mode", ["soft"])


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
    ii_max=None,
    cfg_width=None,
    extra=(),
):
    """Run mocarabe and return the generated rtl directory.

    With device, c=None takes the channel count from the device file.  max_c
    starts at c and raises it until the ILP finds a schedule.  ii_max and
    cfg_width shape the soft bitstream.  extra: more mocarabe arguments.
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
    if ii_max is not None:
        cmd += ["--ii_max", str(ii_max)]
    if cfg_width is not None:
        cmd += ["--cfg_width", str(cfg_width)]
    cmd += ["--place_time", str(place_time), "--sched_method", sched_method, *extra]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=MOCARABE_ROOT)
    assert result.returncode == 0, f"mocarabe failed:\n{result.stdout}\n{result.stderr}"

    # Extract the rtl directory from the output
    match = re.search(r"cd (proj/\S+/rtl/)", result.stdout)
    assert match, f"Could not find rtl dir in mocarabe output:\n{result.stdout}"
    return os.path.join(MOCARABE_ROOT, match.group(1))


def simulate(rtl_dir, mode="hard", trace=False):
    """Compile and run with the hard or soft bitstream.  With trace, the run's
    cycle-by-cycle trace is left in trace_<mode>.txt."""
    assert mode in ("hard", "soft")
    vvp = f"mocarabe_sim_{mode}.vvp"
    defines = f"-DBITSTREAM_SOFT={int(mode == 'soft')}" + (" -DTRACE" if trace else "")
    result = subprocess.run(
        f"iverilog -g2012 {defines} -o {vvp} {RTL_FILES}",
        shell=True, capture_output=True, text=True, cwd=rtl_dir,
    )
    assert result.returncode == 0, f"iverilog failed:\n{result.stderr}"

    result = subprocess.run(["vvp", vvp], capture_output=True, text=True, cwd=rtl_dir)
    if trace:
        os.replace(os.path.join(rtl_dir, "trace.txt"), os.path.join(rtl_dir, f"trace_{mode}.txt"))
    return result.stdout + result.stderr


def run_simulation(dfg, ii, mode="hard", **kwargs):
    return simulate(generate_project(dfg, ii, **kwargs), mode)


def assert_no_errors(sim_output):
    errors = [line for line in sim_output.splitlines() if "Assert error" in line]
    assert not errors, "Simulation assertion failures:\n" + "\n".join(errors)
    assert "=== PASS" in sim_output, "Simulation did not report PASS:\n" + sim_output[-2000:]


def assert_bitstreams_agree(rtl_dir):
    """Both bitstreams pass, and every PE's output and operand inputs match on
    every cycle from run cycle 0."""
    for mode in ("hard", "soft"):
        assert_no_errors(simulate(rtl_dir, mode, trace=True))
    with open(os.path.join(rtl_dir, "trace_hard.txt")) as f:
        hard = f.read().splitlines()
    with open(os.path.join(rtl_dir, "trace_soft.txt")) as f:
        soft = f.read().splitlines()
    assert len(hard) > 20, "trace too short to compare"
    for cycle, (h, s) in enumerate(zip(hard, soft)):
        assert h == s, f"hard and soft differ at run cycle {cycle}:\n  hard {h}\n  soft {s}"
    assert len(hard) == len(soft), "traces have different lengths"


# ── Right-sized benchmarks ────────────────────────────────────────────────────


@HARD
@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_adder_chain_ii1(mode):
    assert_no_errors(run_simulation("hgr/int_adder_chain", ii=1, mode=mode))


@SOFT
@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_adder_chain_ii2(mode):
    assert_no_errors(run_simulation("hgr/int_adder_chain", ii=2, mode=mode))


@HARD
@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_adder_chain_ii3(mode):
    assert_no_errors(run_simulation("hgr/int_adder_chain", ii=3, mode=mode))


@SOFT
@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_adder_chain_ii4(mode):
    output = run_simulation("hgr/int_adder_chain", ii=4, mode=mode, cfg_width=8)
    assert_no_errors(output)


@HARD
@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_poly_quadratic_ii1(mode):
    assert_no_errors(run_simulation("hgr/int_poly_quadratic", ii=1, mode=mode, c=40))


@SOFT
@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_poly_quadratic_ii2(mode):
    output = run_simulation("hgr/int_poly_quadratic", ii=2, mode=mode, c=40, cfg_width=8)
    assert_no_errors(output)


@HARD
@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_poly_quadratic_ii3(mode):
    assert_no_errors(run_simulation("hgr/int_poly_quadratic", ii=3, mode=mode, c=40))


# ── Fixed device flow ─────────────────────────────────────────────────────────
# PE types and layout come from devices/*.json instead of being sized to the DFG.


def expected_peconf(device_file):
    """PECONF hex for a device grid: one nibble per PE, pe_id = x + y*Nx, LSB first"""
    with open(os.path.join(MOCARABE_ROOT, device_file)) as f:
        rows = [row.split() for row in json.load(f)["grid"]]
    op_code = {"+": "0", "*": "1", "IO": "2"}
    pes = [op_code[t] for row in reversed(rows) for t in row]  # first row is the top
    return "".join(reversed(pes))


def generate_fixed_device(dfg, ii, device, **kwargs):
    rtl_dir = generate_project(dfg, ii, c=None, device=device, **kwargs)
    with open(os.path.join(rtl_dir, "benchmark.h")) as f:
        peconf = re.search(r"`define PECONF \d+'h(\w+)", f.read()).group(1)
    assert peconf == expected_peconf(device), "PE types do not match the device file"
    return rtl_dir


@HARD
@pytest.mark.timeout(SIM_TIMEOUT)
def test_fixed_device_int_adder_chain_ii2(mode):
    rtl_dir = generate_fixed_device("hgr/int_adder_chain", 2, "devices/tt_3x3_1mul.json")
    assert_no_errors(simulate(rtl_dir, mode))


@SOFT
@pytest.mark.timeout(SIM_TIMEOUT)
def test_fixed_device_int_poly_quadratic_ii2(mode):
    # both multiplies share the single '*' PE; the chip holds 4 slots but runs 2
    rtl_dir = generate_fixed_device(
        "hgr/int_poly_quadratic", 2, "devices/tt_3x3_1mul.json", ii_max=4
    )
    assert_no_errors(simulate(rtl_dir, mode))


@HARD
@pytest.mark.timeout(SIM_TIMEOUT)
def test_fixed_device_4x4_int_poly_quadratic_ii2(mode):
    rtl_dir = generate_fixed_device("hgr/int_poly_quadratic", 2, "devices/tt_4x4_1mul.json")
    assert_no_errors(simulate(rtl_dir, mode))


# ── Larger benchmarks ─────────────────────────────────────────────────────────
# The scheduling ILP grows with C, so large C runs out of solver time rather than
# being infeasible.  These start at low C and let the scheduler raise it.


@HARD
@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_sobel_ii1(mode):
    # fanout-4 nets; needs cycle-free routing and FIFO-bounded operand timing
    assert_no_errors(run_simulation("hgr/int_sobel", ii=1, mode=mode, c=2, max_c=8))


@HARD
@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_iir8_ii1(mode):
    # outputs y0..y6 also feed later stages; values overflow 32 bits
    assert_no_errors(run_simulation("hgr/int_iir8", ii=1, mode=mode, c=2, max_c=8))


@SOFT
@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_level1_linear_ii1(mode):
    assert_no_errors(run_simulation("hgr/int_level1_linear", ii=1, mode=mode, c=2, max_c=8))


@SOFT
@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_approx1_ii1(mode):
    # T2*T2: one net feeds both ports of the same PE; programmed one bit per clock
    output = run_simulation("hgr/int_approx1", ii=1, mode=mode, c=2, max_c=8, cfg_width=1)
    assert_no_errors(output)


@HARD
@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_poly4_ii1_split_input_fanout(mode):
    # Horner form: x feeds every stage, so one x would wait longer than the
    # 64-deep FIFOs allow; each consumer gets its own copy of x instead
    output = run_simulation(
        "hgr/int_poly4", ii=1, mode=mode, c=2, max_c=8, split_input_fanout=True
    )
    assert_no_errors(output)


# ── Hard and soft bitstreams agree ────────────────────────────────────────────
# One generated project, simulated with each bitstream: both pass and every PE's
# output and operand inputs are identical on every cycle once configured.


@pytest.mark.timeout(2 * SIM_TIMEOUT)
def test_bitstreams_agree_int_adder_chain_ii2_whole_frame_words():
    # C=20 gives 142-bit frames; one word per frame
    rtl_dir = generate_project("hgr/int_adder_chain", 2, cfg_width=142)
    assert_bitstreams_agree(rtl_dir)


@pytest.mark.timeout(2 * SIM_TIMEOUT)
def test_bitstreams_agree_int_sobel_ii1_one_bit_words():
    rtl_dir = generate_project("hgr/int_sobel", 1, c=2, max_c=8, cfg_width=1)
    assert_bitstreams_agree(rtl_dir)


@pytest.mark.timeout(2 * SIM_TIMEOUT)
def test_bitstreams_agree_fixed_device_programmable_ii():
    rtl_dir = generate_fixed_device(
        "hgr/int_poly_quadratic", 2, "devices/tt_3x3_1mul.json", ii_max=4, cfg_width=8
    )
    assert_bitstreams_agree(rtl_dir)


# ── The soft bitstream really configures the chip ─────────────────────────────


@pytest.mark.timeout(SIM_TIMEOUT)
def test_corrupt_soft_bitstream_fails():
    """Flip one bit of an SRL read address a compute PE uses: the soft run must fail."""
    rtl_dir = generate_project("hgr/int_adder_chain", 2, c=2, max_c=8, cfg_width=8)
    assert_no_errors(simulate(rtl_dir, "soft"))

    frames, layout = read_frames(rtl_dir)
    fields = layout["frame_fields"]
    offset = dict((name, sum(w for _, w in fields[:i])) for i, (name, _) in enumerate(fields))
    width = dict(fields)
    with open(os.path.join(rtl_dir, "benchmark.h")) as f:
        peconf = re.search(r"`define PECONF \d+'h(\w+)", f.read()).group(1)
    ops = list(reversed(peconf))  # PE type per pe_idx
    first_pe_row = 1 + layout["ii_max"]  # after the global row and the output rows
    for row in range(first_pe_row, len(frames)):
        pe = (row - first_pe_row) // layout["ii_max"]
        addr = (frames[row] >> offset["op1_addr"]) & (2 ** width["op1_addr"] - 1)
        if ops[pe] in "01" and addr:  # an adder or multiplier slot that reads its FIFO
            frames[row] ^= 1 << offset["op1_addr"]
            break
    else:
        pytest.fail("no compute PE reads its op1 FIFO")

    cfg_width, wpf = layout["cfg_width"], layout["words_per_frame"]
    words = [(f >> (k * cfg_width)) & (2**cfg_width - 1) for f in frames for k in reversed(range(wpf))]
    with open(os.path.join(rtl_dir, "bitstream.hex"), "w") as f:
        f.write("".join(f"{w:0{-(-cfg_width // 4)}x}\n" for w in words))

    output = simulate(rtl_dir, "soft")
    assert "=== FAIL" in output, "a corrupted SRL address did not change the result"


@pytest.mark.timeout(2 * SIM_TIMEOUT)
def test_soft_bitstream_reprograms_one_chip(tmp_path):
    """Two kernels at different II on the same device build identical soft-mode
    hardware, so a chip built for one runs the other from its bitstream."""
    device = "devices/tt_3x3_1mul.json"
    chip = generate_fixed_device("hgr/int_adder_chain", 2, device, ii_max=4, cfg_width=8)
    other = generate_fixed_device("hgr/int_poly_quadratic", 3, device, ii_max=4, cfg_width=8)

    sources = [f for f in os.listdir(chip) if f.endswith((".v", ".sv")) and not f.endswith("_tb.sv")]
    for f in sources:
        with open(os.path.join(chip, f)) as a, open(os.path.join(other, f)) as b:
            assert a.read() == b.read(), f"{f} differs between the two kernels"

    reprogrammed = tmp_path / "chip"
    reprogrammed.mkdir()
    for f in sources + ["benchmark.h", "mocarabe.h"]:
        shutil.copy(os.path.join(chip, f), reprogrammed)
    for f in ("mocarabe_tb.sv", "bitstream.hex"):  # the other kernel's program and checks
        shutil.copy(os.path.join(other, f), reprogrammed)
    assert_no_errors(simulate(str(reprogrammed), "soft"))



# ── Chip-sized datapaths and shared IO (the TinyTapeout demo) ─────────────────

# The demo: level1_linear packed into a 2x2 array at II=4.  Its four inputs share
# one input bus and its output reaches io_out, each in its own slot; 8-bit data,
# 16-deep FIFOs and a 2-stage PE pipeline.
DEMO = dict(
    dfg="hgr/int_level1_linear",
    ii=4,
    iod=4,
    ard=4,
    c=2,
    max_c=6,
    cfg_width=8,
    extra=[
        "--shared_io", "--data_width", "8", "--fifo_depth", "16", "--pe_pipe", "2",
        "--bitstream", "soft",
    ],
)


def generate_demo():
    return generate_project(**DEMO)


@pytest.mark.timeout(2 * SIM_TIMEOUT)
def test_bitstreams_agree_shared_io_demo():
    rtl_dir = generate_demo()
    with open(os.path.join(rtl_dir, "benchmark.h")) as f:
        header = f.read()
    for define in ("BENCHMARK_DATA_WIDTH 8", "FIFO_DEPTH 16", "PE_PIPE_NUM 2", "BENCHMARK_X_WIDTH 2"):
        assert define in header
    with open(os.path.join(rtl_dir, "mocarabe_tb.sv")) as f:
        assert "assert(io_out ==" in f.read(), "the output port is not checked"

    with open(os.path.join(rtl_dir, "io_schedule.json")) as f:
        schedule = json.load(f)
    slots = [i["cycle"] % schedule["ii"] for i in schedule["inputs"]]
    assert len(slots) == 4 and len(set(slots)) == 4, "inputs share a slot of the input bus"
    assert len(schedule["outputs"]) == 1
    assert_bitstreams_agree(rtl_dir)


@SOFT
@pytest.mark.timeout(SIM_TIMEOUT)
def test_int_adder_chain_ii2_8bit_fifo16(mode):
    output = run_simulation(
        "hgr/int_adder_chain", 2, mode=mode, c=2, max_c=8, cfg_width=8,
        extra=["--data_width", "8", "--fifo_depth", "16"],
    )
    assert_no_errors(output)


def test_shared_io_needs_a_slot_per_input():
    # poly_quadratic has four inputs (two are constants) and II=2 has two slots
    cmd = [
        "python3", "-m", "mocarabe", "-dfg", "hgr/int_poly_quadratic", "-II", "2",
        "-C", "2", "--shared_io", "--place_time", "0.1", "--sched_method", "ILP",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=MOCARABE_ROOT)
    assert result.returncode != 0
    assert "4 inputs need their own slots but II is 2" in result.stderr
