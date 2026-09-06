import os
import subprocess
import pytest


@pytest.mark.eda
def test_lint(plain_jane_arch_dir):
    verilog_files = []

    for root, _, files in os.walk(plain_jane_arch_dir):
        for filename in files:
            if filename.endswith((".v", ".sv")):
                verilog_files.append(os.path.join(root, filename))

    assert verilog_files, f"No Verilog files found in {plain_jane_arch_dir}"

    cmd = [
        "slang",
        "--lint-only",
        "-I",
        plain_jane_arch_dir,
        "+define+USE_SYSTEMVERILOG",
    ] + verilog_files

    lint_result = subprocess.run(cmd, capture_output=True, text=True)

    assert lint_result.returncode == 0, (
        f"Linting failed:\n\n"
        f"STDOUT:\n{lint_result.stdout}\n"
        f"STDERR:\n{lint_result.stderr}"
    )
