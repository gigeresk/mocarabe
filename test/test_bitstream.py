import random

import pytest

from mocarabe.rtl_gen.bitstream_gen import (
    frame_fields,
    out_fields,
    pe_slot_values,
    read_frames,
    write_bitstream,
)


def write_dat_files(rtl_dir, Nx, Ny, C, II, seed=0, fifo_depth=64):
    """Random schedule memories in the formats the hard bitstream's .dat files use;
    returns the output rows"""
    rng = random.Random(seed)
    _, out_w = out_fields(Nx * Ny)
    out_rows = [rng.randrange(2**out_w) for _ in range(II)]
    (rtl_dir / "io_out_memory.dat").write_text("".join(format(r, f"0{out_w}b") + "\n" for r in out_rows))
    for x in range(Nx):
        for y in range(Ny):
            for c in range(C):
                for kind in ("n", "e", "pe"):
                    values = [format(rng.randrange(4), "02b") for _ in range(II)]
                    (rtl_dir / f"noc_memory_{kind}_x{x}_y{y}_c{c}.dat").write_text("\n".join(values) + "\n")
            for operand in (1, 2):
                values = [format(rng.randrange(fifo_depth), "x") for _ in range(II)]
                (rtl_dir / f"op{operand}_addr_memory_x{x}_y{y}.dat").write_text("\n".join(values) + "\n")
            for port in (0, 1):
                values = [format(rng.randrange(C), "b") for _ in range(II)]
                (rtl_dir / f"pe_mux_x{x}_y{y}_sel_mem{port}.dat").write_text("\n".join(values) + "\n")
    return out_rows


def unpack(frame, fields):
    values, offset = {}, 0
    for name, width in fields:
        values[name] = (frame >> offset) & (2**width - 1)
        offset += width
    return values


@pytest.mark.parametrize("cfg_width", [1, 3, 8, 32, 64])
@pytest.mark.parametrize("fifo_depth", [16, 64])
def test_bitstream_round_trip(tmp_path, cfg_width, fifo_depth):
    Nx, Ny, C, II, ii_max = 2, 2, 3, 2, 3
    out_rows = write_dat_files(tmp_path, Nx, Ny, C, II, fifo_depth=fifo_depth)
    words = write_bitstream(str(tmp_path), Nx, Ny, C, II, ii_max, cfg_width, fifo_depth)

    frames, layout = read_frames(str(tmp_path))
    fields, frame_w = frame_fields(C, fifo_depth)
    addr_w = (fifo_depth - 1).bit_length()
    assert layout["frame_width"] == frame_w == 6 * C + 2 * addr_w + 2 * 2
    assert len(frames) == 1 + ii_max + Nx * Ny * ii_max
    assert words == len(frames) * -(-frame_w // cfg_width)
    assert frames[0] == II - 1  # global row
    # output rows, padded to ii_max slots
    assert frames[1 : 1 + ii_max] == out_rows + [0] * (ii_max - II)

    for p in range(Nx * Ny):
        expected = pe_slot_values(str(tmp_path), p % Nx, p // Nx, C, II)
        for t in range(ii_max):
            got = unpack(frames[1 + ii_max + p * ii_max + t], fields)
            for name, _ in fields:
                assert got[name] == (expected[name][t] if t < II else 0), (p, t, name)


def test_word_lines_fit_cfg_width(tmp_path):
    write_dat_files(tmp_path, 1, 1, 2, 1)
    write_bitstream(str(tmp_path), 1, 1, 2, 1, 1, 5)
    for line in (tmp_path / "bitstream.hex").read_text().split():
        assert int(line, 16) < 2**5


def test_ii_max_below_ii_rejected(tmp_path):
    write_dat_files(tmp_path, 1, 1, 2, 3)
    with pytest.raises(AssertionError, match="smaller than II"):
        write_bitstream(str(tmp_path), 1, 1, 2, 3, 2, 1)
