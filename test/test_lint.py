import os
import subprocess
import pytest


@pytest.fixture
def plain_jane_arch() -> str:
    from src.mocarabe.cli import main

    rtl_dir = main(
        [
            "-dfg",
            "hgr/int_adder_chain",
            "-II",
            "1",
            "-C",
            "20",
            "-iod",
            "1",
            "-ard",
            "1",
            "--sched_method",
            "ILP",
        ]
    )
    return rtl_dir


@pytest.mark.eda
def test_lint(plain_jane_arch):
    verilog_files = []

    for root, _, files in os.walk(plain_jane_arch):
        for filename in files:
            if filename.endswith((".v", ".sv")):
                verilog_files.append(os.path.join(root, filename))

    assert verilog_files, f"No Verilog files found in {plain_jane_arch}"

    cmd = [
        "slang",
        "--lint-only",
        "-I",
        plain_jane_arch,
        "+define+USE_SYSTEMVERILOG",
    ] + verilog_files

    lint_result = subprocess.run(cmd, capture_output=True, text=True)

    assert lint_result.returncode == 0, (
        f"Linting failed:\n\n"
        f"STDOUT:\n{lint_result.stdout}\n"
        f"STDERR:\n{lint_result.stderr}"
    )
