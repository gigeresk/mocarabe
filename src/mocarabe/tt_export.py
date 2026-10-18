"""Export a generated project to a TinyTapeout project (a ttsky-verilog-template clone).

    python -m mocarabe.tt_export proj/<name>/rtl/ ../ttsky-verilog-mocarabe --tiles 2x2

The project must use the soft bitstream and shared IO, with data and configuration
words of at most 8 bits:

    python -m mocarabe -dfg hgr/int_level1_linear -II 4 -iod 4 -ard 4 -C 2 --max_C 6 \\
        --sched_method ILP --shared_io --data_width 8 --fifo_depth 16 --pe_pipe 2 \\
        --bitstream soft --cfg_width 8

The export copies the RTL and tt_um_gigeresk_mocarabe.v into src/, the bitstream and
the kernel's IO schedule into test/ with a cocotb test that programs the chip and
checks its outputs, and fills in info.yaml, test/Makefile, test/tb.v and docs/info.md.
"""

import argparse
import json
import os
import re
import shutil

from mocarabe.rtl_gen.testbench_gen import flush_cycles

TT_RTL = os.path.join(os.path.dirname(__file__), "..", "..", "rtl", "tt")
TOP = "tt_um_gigeresk_mocarabe"
SOURCES = [
    f"{TOP}.v",
    "mocarabe.sv",
    "torus_switch.sv",
    "pe_2_input.sv",
    "pe_mux_n_input.sv",
    "pe_srl.v",
    "SRL16E.v",
    "SRLC32E.v",
    "SRL64.v",
    "cfg_loader.sv",
    "cfg_row.sv",
    "pe_cfg.sv",
]
HEADERS = ["benchmark.h", "mocarabe.h"]
TILES = ("1x1", "1x2", "2x2", "3x2", "4x2", "6x2", "8x2")

PINOUT = {
    "ui[{i}]": "cfg_data[{i}] / in[{i}]",
    "uo[{i}]": "out[{i}]",
}
UIO = {0: "cfg_en", 1: "out_valid"}


def read_defines(path):
    with open(path) as f:
        return dict(re.findall(r"`define\s+(\w+)\s+(\S+)", f.read()))


def replace_line(text, key, value):
    """Set a `  key: value` line of info.yaml, keeping its comment"""
    pattern = re.compile(rf"^(\s*{re.escape(key)}:\s*)(\"[^\"]*\"|\S+)", re.M)
    assert pattern.search(text), f"info.yaml has no {key}"
    return pattern.sub(lambda m: m.group(1) + value, text, count=1)


def write_info_yaml(path, defines, tiles, kernel):
    with open(path) as f:
        text = f.read()
    text = replace_line(text, "title", '"Mocarabe: a programmable time-multiplexed CGRA"')
    text = replace_line(text, "author", '"Fred Tombs"')
    text = replace_line(
        text,
        "description",
        f'"{defines["BENCHMARK_X_WIDTH"]}x{defines["BENCHMARK_Y_WIDTH"]} torus of '
        f'{defines["BENCHMARK_DATA_WIDTH"]}-bit PEs, configured serially (demo: {kernel})"',
    )
    text = replace_line(text, "language", '"SystemVerilog"')
    text = replace_line(text, "clock_hz", "50000000")
    text = replace_line(text, "tiles", f'"{tiles}"')
    text = replace_line(text, "top_module", f'"{TOP}"')
    sources = "".join(f'    - "{s}"\n' for s in SOURCES)
    text, n = re.subn(r"(  source_files:\n)(    - \"[^\"]*\"\n)+", lambda m: m.group(1) + sources, text)
    assert n == 1, "info.yaml has no source_files list"

    d_w, cfg_w = int(defines["BENCHMARK_DATA_WIDTH"]), int(defines["CFG_WIDTH"])
    pins = {}
    for i in range(8):
        roles = ([f"cfg_data[{i}]"] if i < cfg_w else []) + ([f"in[{i}]"] if i < d_w else [])
        pins[f"ui[{i}]"] = " / ".join(roles)
        pins[f"uo[{i}]"] = f"out[{i}]" if i < d_w else ""
        pins[f"uio[{i}]"] = UIO.get(i, "")
    for pin, name in pins.items():
        text = replace_line(text, pin, f'"{name}"')
    with open(path, "w") as f:
        f.write(text)


def write_docs(path, defines, program, kernel, words):
    ii = program["ii"]
    inputs = ", ".join(f"`{i['name']}` at cycle {i['cycle']}" for i in program["inputs"])
    outputs = ", ".join(f"`{o['label']}` at cycle {o['cycle']}" for o in program["outputs"])
    text = f"""## How it works

Mocarabe is a coarse-grained reconfigurable array: a
{defines["BENCHMARK_X_WIDTH"]}x{defines["BENCHMARK_Y_WIDTH"]} torus of processing elements
(adders, multipliers and IO PEs) joined by a time-multiplexed network with
{defines["BENCHMARK_CHAN_WIDTH"]} channels per link. Every {defines["BENCHMARK_DATA_WIDTH"]}-bit
value moves through scheduled switches and waits in a {defines["FIFO_DEPTH"]}-deep FIFO at
its consumer. A kernel's dataflow graph is placed and scheduled offline by the
Mocarabe toolchain into a modulo schedule of II cycles (up to II_MAX =
{defines["BENCHMARK_II_MAX"]}), which is loaded at run time as a serial bitstream. The
chip starts a new iteration of the kernel every II cycles.

The bundled demo is `{kernel}` at II = {ii}: {len(program["inputs"])} inputs and
{len(program["outputs"])} output share the input and output pins, each in its own slot.

## How to test

1. Hold `rst_n` low and `cfg_en` (`uio[0]`) low for at least one clock.
2. Raise `cfg_en` and present one word of `test/bitstream.hex` on `ui_in` per clock
   ({words} words, {defines["CFG_WIDTH"]} bits each), then drop `cfg_en`.
3. Keep `rst_n` low with `ui_in` at 0 for {program["flush_cycles"]} clocks, then release it.
   The first rising edge with `rst_n` high is run cycle 0.
4. Iteration k of each input is sampled from `ui_in` at run cycle `cycle + k*{ii}`:
   {inputs}.
5. Iteration k of each output is on `uo_out` at run cycle `cycle + k*{ii}`, with
   `out_valid` (`uio[1]`) high: {outputs}.

`test/test.py` does exactly this for 16 iterations of random inputs and checks
every output against the dataflow graph in `test/mocarabe_program.json`.

## External hardware

None: the RP2040 on the demo board can drive the bitstream and inputs.
"""
    with open(path, "w") as f:
        f.write(text)


def export(rtl_dir, tt_dir, tiles):
    defines = read_defines(os.path.join(rtl_dir, "benchmark.h"))
    assert defines.get("BITSTREAM_SOFT") == "1", "generate the project with --bitstream soft"
    assert int(defines["BENCHMARK_DATA_WIDTH"]) <= 8, "the pins carry at most 8 data bits: --data_width 8"
    assert int(defines["CFG_WIDTH"]) <= 8, "the pins carry at most 8 configuration bits: --cfg_width 8"
    schedule_path = os.path.join(rtl_dir, "io_schedule.json")
    assert os.path.exists(schedule_path), "generate the project with --shared_io"
    assert tiles in TILES, f"tiles must be one of {TILES}"

    src, test = os.path.join(tt_dir, "src"), os.path.join(tt_dir, "test")
    for name in SOURCES[1:] + HEADERS:
        shutil.copy(os.path.join(rtl_dir, name), os.path.join(src, name))
    shutil.copy(os.path.join(TT_RTL, f"{TOP}.v"), os.path.join(src, f"{TOP}.v"))
    if os.path.exists(os.path.join(src, "project.v")):
        os.remove(os.path.join(src, "project.v"))  # the template's example design

    with open(schedule_path) as f:
        program = json.load(f)
    program["cfg_width"] = int(defines["CFG_WIDTH"])
    program["flush_cycles"] = flush_cycles(program["fifo_depth"])
    with open(os.path.join(test, "mocarabe_program.json"), "w") as f:
        json.dump(program, f, indent=2)
    shutil.copy(os.path.join(rtl_dir, "bitstream.hex"), os.path.join(test, "bitstream.hex"))
    shutil.copy(os.path.join(TT_RTL, "test.py"), os.path.join(test, "test.py"))
    with open(os.path.join(rtl_dir, "bitstream.hex")) as f:
        words = len(f.read().split())

    makefile = os.path.join(test, "Makefile")
    with open(makefile) as f:
        text = f.read()
    text = re.sub(r"^PROJECT_SOURCES = .*$", f"PROJECT_SOURCES = {' '.join(SOURCES)}", text, flags=re.M)
    if "MOCARABE_QUIET" not in text:  # no per-cycle PE and switch prints in the test log
        text = text.replace(
            "COMPILE_ARGS \t\t+= -I$(SRC_DIR)\n",
            "COMPILE_ARGS \t\t+= -I$(SRC_DIR)\nCOMPILE_ARGS \t\t+= -DMOCARABE_QUIET\n",
        )
        assert "MOCARABE_QUIET" in text, "test/Makefile has no -I$(SRC_DIR) line"
    with open(makefile, "w") as f:
        f.write(text)

    tb = os.path.join(test, "tb.v")
    with open(tb) as f:
        text = f.read()
    text = re.sub(r"\btt_um_\w+ user_project", f"{TOP} user_project", text)
    with open(tb, "w") as f:
        f.write(text)

    hgr = [n for n in os.listdir(os.path.join(rtl_dir, "..", "hgr")) if n.endswith(".hgr")]
    kernel = hgr[0][: -len(".hgr")] if hgr else "kernel"
    write_info_yaml(os.path.join(tt_dir, "info.yaml"), defines, tiles, kernel)
    write_docs(os.path.join(tt_dir, "docs", "info.md"), defines, program, kernel, words)
    return kernel, words


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("rtl_dir", help="a generated project's rtl/ directory")
    parser.add_argument("tt_dir", help="the TinyTapeout project to write into")
    parser.add_argument("--tiles", default="2x2", help=f"TinyTapeout tiles, one of {TILES}")
    args = parser.parse_args(argv)
    kernel, words = export(args.rtl_dir, args.tt_dir, args.tiles)
    print(f"Exported {kernel} ({words} configuration words) to {args.tt_dir}")


if __name__ == "__main__":
    main()
