import os
from pathlib import Path

import pytest
from siliconcompiler import Design

REPO_ROOT = Path(__file__).resolve().parent


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


def pytest_generate_tests(metafunc):
    # one test case per file for tests that take these arguments
    files = {
        "int_dfg_path": sorted(REPO_ROOT.glob("hgr/int_*/int_*.hgr")),
        "device_file": sorted(REPO_ROOT.glob("devices/*.json")),
    }
    for arg, paths in files.items():
        if arg in metafunc.fixturenames:
            metafunc.parametrize(arg, paths, ids=[p.stem for p in paths])

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
    # SC runs synthesis in its own build dir, so point $readmem at the generated schedule files
    dat_dir = os.path.abspath(plain_jane_arch_dir)
    design.add_define(f'MOCARABE_DAT_DIR="{dat_dir}/"', fileset="rtl")
    # SC preprocesses in its elaborate step, before yosys adds its own -D SYNTHESIS
    design.add_define("SYNTHESIS", fileset="rtl")
    for root, _, files in os.walk(plain_jane_arch_dir):
        for filename in files:
            full_path = os.path.join(root, filename)
            # .dat files are read via $readmem and .h files via `include, not compiled directly
            if filename.endswith(('.dat', '.h')):
                continue
            design.add_file(filename=full_path, fileset="rtl")
    return design