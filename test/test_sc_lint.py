import os
import pytest
from siliconcompiler import Design
from siliconcompiler.flows.lintflow import LintFlow
from siliconcompiler.asic import ASIC
from siliconcompiler.targets import asap7_demo


@pytest.fixture
def plain_jane_arch() -> Design:
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

    design = Design("mocarabe")
    design.set_topmodule("mocarabe", "rtl")
    for root, _, files in os.walk(rtl_dir):
        for filename in files:
            full_path = os.path.join(root, filename)
            design.add_file(filename=full_path, fileset="rtl")
    return design


@pytest.mark.eda
def test_sc_lint(plain_jane_arch):

    asic = ASIC(plain_jane_arch)

    asic.add_fileset("rtl")

    asap7_demo(asic)  # diff targets
    asic.set_flow(LintFlow())  # also SlangLintFlow, VerilatorLintFlow

    asic.run()
