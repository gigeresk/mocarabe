# Export the demo to a TinyTapeout project and check what lands there: the
# template's files filled in, and sources that compile with the template's testbench
# (iverilog) and with the yosys frontend TinyTapeout synthesizes with.

import json
import os
import shutil
import subprocess

import pytest

from mocarabe.tt_export import SOURCES, TOP, export
from test_simulation import SIM_TIMEOUT, generate_demo

# The parts of ttsky-verilog-template the export rewrites, as the template has them
INFO_YAML = """# Tiny Tapeout project information
project:
  title:        ""      # Project title
  author:       ""      # Your name
  discord:      ""      # Your discord username
  description:  ""      # One line description of what your project does
  language:     "Verilog" # other examples include SystemVerilog, Amaranth, VHDL, etc
  clock_hz:     0       # Clock frequency in Hz (or 0 if not applicable)
  tiles: "1x1"          # Valid values: 1x1, 1x2, 2x2, 3x2, 4x2, 6x2 or 8x2
  top_module:  "tt_um_example"
  source_files:
    - "project.v"

pinout:
""" + "".join(f'  {bus}[{i}]: ""\n' for bus in ("ui", "uo", "uio") for i in range(8)) + """
yaml_version: 6
"""
MAKEFILE = """SRC_DIR = $(PWD)/../src
PROJECT_SOURCES = project.v
VERILOG_SOURCES += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))
COMPILE_ARGS \t\t+= -I$(SRC_DIR)
VERILOG_SOURCES += $(PWD)/tb.v
"""
TB = """`default_nettype none
`timescale 1ns / 1ps
module tb ();
  reg clk;
  reg rst_n;
  reg ena;
  reg [7:0] ui_in;
  reg [7:0] uio_in;
  wire [7:0] uo_out;
  wire [7:0] uio_out;
  wire [7:0] uio_oe;
  tt_um_example user_project (
      .ui_in(ui_in), .uo_out(uo_out), .uio_in(uio_in), .uio_out(uio_out),
      .uio_oe(uio_oe), .ena(ena), .clk(clk), .rst_n(rst_n)
  );
endmodule
"""


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    tt = tmp_path_factory.mktemp("tt")
    for d in ("src", "test", "docs"):
        (tt / d).mkdir()
    (tt / "info.yaml").write_text(INFO_YAML)
    (tt / "src" / "project.v").write_text("module tt_um_example; endmodule\n")
    (tt / "test" / "Makefile").write_text(MAKEFILE)
    (tt / "test" / "tb.v").write_text(TB)
    (tt / "docs" / "info.md").write_text("## How it works\n")
    export(generate_demo(), str(tt), "3x2")
    return tt


@pytest.mark.timeout(2 * SIM_TIMEOUT)
def test_export_fills_in_the_template(exported):
    info = (exported / "info.yaml").read_text()
    assert f'top_module:  "{TOP}"' in info
    assert 'tiles: "3x2"' in info
    assert 'language:     "SystemVerilog"' in info
    for source in SOURCES:
        assert f'    - "{source}"' in info
        assert (exported / "src" / source).exists()
    assert 'ui[0]: "cfg_data[0] / in[0]"' in info
    assert 'uio[0]: "cfg_en"' in info and 'uio[1]: "out_valid"' in info
    assert not (exported / "src" / "project.v").exists()

    makefile = (exported / "test" / "Makefile").read_text()
    assert f"PROJECT_SOURCES = {' '.join(SOURCES)}" in makefile
    assert "-DMOCARABE_QUIET" in makefile
    assert f"{TOP} user_project" in (exported / "test" / "tb.v").read_text()

    program = json.loads((exported / "test" / "mocarabe_program.json").read_text())
    assert program["cfg_width"] == 8 and program["data_width"] == 8
    assert program["flush_cycles"] == 2 * 16 + 16
    assert (exported / "test" / "test.py").exists()
    assert (exported / "test" / "bitstream.hex").exists()


@pytest.mark.timeout(SIM_TIMEOUT)
def test_exported_sources_compile_with_the_testbench(exported):
    sources = [str(exported / "src" / s) for s in SOURCES] + [str(exported / "test" / "tb.v")]
    result = subprocess.run(
        ["iverilog", "-g2012", "-DMOCARABE_QUIET", "-I", str(exported / "src"),
         "-s", "tb", "-o", str(exported / "tb.vvp"), *sources],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.eda
@pytest.mark.timeout(10 * SIM_TIMEOUT)
@pytest.mark.skipif(shutil.which("yosys") is None, reason="needs yosys")
def test_exported_sources_parse_with_yosys(exported):
    # TinyTapeout synthesizes with yosys's own SystemVerilog frontend, not slang
    src = exported / "src"
    script = f"read_verilog -sv {' '.join(SOURCES)}; hierarchy -check -top {TOP}; proc"
    result = subprocess.run(["yosys", "-q", "-p", script], capture_output=True, text=True, cwd=src)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.eda
@pytest.mark.timeout(SIM_TIMEOUT)
@pytest.mark.skipif(shutil.which("verilator") is None, reason="needs verilator")
def test_exported_sources_pass_the_linter(exported):
    # TinyTapeout's flow lints with Verilator first, without SYNTHESIS defined, and
    # stops on any error (warnings are reported only)
    result = subprocess.run(
        ["verilator", "--lint-only", "-Wall", "-Wno-fatal", "-Wno-DECLFILENAME",
         "--top-module", TOP, *SOURCES],
        capture_output=True, text=True, cwd=exported / "src",
    )
    errors = [line for line in result.stderr.splitlines() if line.startswith("%Error")]
    assert not errors, "\n".join(errors)
