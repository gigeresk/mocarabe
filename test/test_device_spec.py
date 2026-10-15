import pytest

from mocarabe.cad.netlist import Netlist
from mocarabe.device import check_dfg_fits, load_device_spec
from mocarabe.device.spec import parse_device_spec


def netlist(repo_root, benchmark):
    return Netlist(str(repo_root / "hgr" / benchmark / f"{benchmark}.hgr"))


def test_load_example_device(repo_root):
    spec = load_device_spec(repo_root / "devices/tt_3x3_1mul.json")
    assert (spec.name, spec.Nx, spec.Ny, spec.channels) == ("tt_3x3_1mul", 3, 3, 2)
    # first grid row is the top of the array (highest y)
    assert spec.device_map[0][2] == "IO"
    assert spec.device_map[1][1] == "*"
    assert spec.device_map[2][0] == "+"


def test_all_devices_load(device_file):
    load_device_spec(device_file)


def test_non_square_grid():
    spec = parse_device_spec({"grid": ["IO + + IO", "+ * + +"], "channels": 3})
    assert (spec.Nx, spec.Ny, spec.channels) == (4, 2, 3)
    assert spec.device_map[3][1] == "IO"
    assert spec.device_map[1][0] == "*"


@pytest.mark.parametrize(
    "data, message",
    [
        ({"grid": ["IO +", "+"]}, "row 1 has 1 cells"),
        ({"grid": ["IO -", "+ +"]}, "unknown PE type '-'"),
        ({"grid": ["IO +", "+ *"], "channels": 1}, "'channels' must be"),
        ({"grid": []}, "'grid' must be"),
        ({"grid": ["IO +", "+ *"], "ii_max": 0}, "'ii_max' must be"),
    ],
)
def test_bad_device(data, message):
    with pytest.raises(ValueError, match=message):
        parse_device_spec(data)


def test_dfg_fits_needs_ii_for_shared_multiplier(repo_root):
    spec = load_device_spec(repo_root / "devices/tt_3x3_1mul.json")
    dfg = netlist(repo_root, "int_poly_quadratic")  # 2 multiplies, 5 IO nodes
    with pytest.raises(ValueError, match=r"2 '\*' nodes need II >= 2"):
        check_dfg_fits(spec, dfg, II=1)
    check_dfg_fits(spec, dfg, II=2)


def test_dfg_needs_missing_pe_type(repo_root):
    spec = parse_device_spec({"grid": ["IO +", "+ IO"]})
    with pytest.raises(ValueError, match=r"has no '\*' PEs"):
        check_dfg_fits(spec, netlist(repo_root, "int_poly_quadratic"), II=4)


def test_ii_max_optional():
    assert parse_device_spec({"grid": ["IO +", "+ *"]}).ii_max is None
    assert parse_device_spec({"grid": ["IO +", "+ *"], "ii_max": 4}).ii_max == 4
