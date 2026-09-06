import os
import pytest
from siliconcompiler import Design

@pytest.fixture
def plain_jane_arch_dir() -> str:
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

@pytest.fixture
def plain_jane_arch(plain_jane_arch_dir) -> Design:

    design = Design("mocarabe")
    design.set_topmodule("mocarabe", "rtl")
    for root, _, files in os.walk(plain_jane_arch_dir):
        for filename in files:
            full_path = os.path.join(root, filename)
            if 'dat' in filename:
                continue
            elif filename.endswith('.h'):
                continue
            design.add_file(filename=full_path, fileset="rtl")
    return design