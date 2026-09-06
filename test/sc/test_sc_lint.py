import pytest
from siliconcompiler import Design
from siliconcompiler.flows.lintflow import LintFlow
from siliconcompiler.asic import ASIC
from siliconcompiler.targets import asap7_demo


@pytest.mark.eda
def test_sc_lint(plain_jane_arch):

    asic = ASIC(plain_jane_arch)

    asic.add_fileset("rtl")

    asap7_demo(asic)  # diff targets
    asic.set_flow(LintFlow())  # also SlangLintFlow, VerilatorLintFlow

    asic.run()
