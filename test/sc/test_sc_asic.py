import pytest
from siliconcompiler.asic import ASIC
from siliconcompiler.targets import asap7_demo, skywater130_demo
from siliconcompiler.tools.yosys.syn_asic import ASICSynthesis


@pytest.mark.eda
@pytest.mark.skip(reason="Need tools dir")
def test_sc_asap7(plain_jane_arch):

    asic = ASIC(plain_jane_arch)

    asic.add_fileset("rtl")

    asap7_demo(asic)

    ASICSynthesis.find_task(asic).set_yosys_useslang(True)

    asic.run()


@pytest.mark.eda
@pytest.mark.skip(reason="Need tools dir")
def test_sc_skywater130(plain_jane_arch):

    asic = ASIC(plain_jane_arch)

    asic.add_fileset("rtl")

    skywater130_demo(asic)

    ASICSynthesis.find_task(asic).set_yosys_useslang(True)

    asic.run()

