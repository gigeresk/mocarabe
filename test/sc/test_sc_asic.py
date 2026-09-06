import pytest
from siliconcompiler.asic import ASIC
from siliconcompiler.targets import asap7_demo
from siliconcompiler.tools.yosys.syn_asic import ASICSynthesis


@pytest.mark.eda
@pytest.skip.reason("Need tools dir")
def test_sc_asap7(plain_jane_arch):

    asic = ASIC(plain_jane_arch)

    asic.add_fileset("rtl")

    asap7_demo(asic)  # diff targets

    ASICSynthesis.find_task(asic).set_yosys_useslang(True)

    asic.run()
