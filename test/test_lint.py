import os
import subprocess
import pytest


@pytest.mark.eda
@pytest.mark.parametrize("mode", ["hard", "soft"])
def test_lint(plain_jane_arch_dir, mode):
    # Every project carries both bitstreams; check the RTL each one selects.
    # Full elaboration from the testbench, not --lint-only: that skips the
    # hierarchy, so code inside generate branches (e.g. the soft bitstream's)
    # is never checked.
    verilog_files = []

    for root, _, files in os.walk(plain_jane_arch_dir):
        for filename in files:
            if filename.endswith((".v", ".sv")):
                verilog_files.append(os.path.join(root, filename))

    assert verilog_files, f"No Verilog files found in {plain_jane_arch_dir}"

    cmd = [
        "slang",
        "--top",
        "mocarabe_tb",
        "-I",
        plain_jane_arch_dir,
        "+define+USE_SYSTEMVERILOG",
        f"+define+BITSTREAM_SOFT={int(mode == 'soft')}",
        "+define+TRACE",
    ] + verilog_files

    lint_result = subprocess.run(cmd, capture_output=True, text=True)

    assert lint_result.returncode == 0, (
        f"Linting failed:\n\n"
        f"STDOUT:\n{lint_result.stdout}\n"
        f"STDERR:\n{lint_result.stderr}"
    )
