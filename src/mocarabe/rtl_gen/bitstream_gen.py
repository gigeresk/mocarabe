"""Soft bitstream: pack the schedule memories into a serial configuration stream.

The stream is what a host sends on cfg_data[CFG_WIDTH-1:0] while cfg_en is high
(see rtl/rtl/cfg_loader.sv).  It is a sequence of frames, one per configuration
row, each padded at the top to a whole number of CFG_WIDTH-bit words and sent
most significant word first:

  row 0:  global row, bits [ii_w-1:0] = II - 1
  then, for every PE p = x + y*Nx in order, for every slot t in 0..II_MAX-1:
      per channel c:  [6c+1:6c] north select, [6c+3:6c+2] east, [6c+5:6c+4] to-PE
      op1 SRL address (ADDR_W bits), op2 SRL address (ADDR_W bits)
      PE fan-in mux select for port 0 (SEL_W bits), port 1 (SEL_W bits)
  Slots II..II_MAX-1 are zero.

The fields come from the .dat files the hard bitstream loads with $readmem, so
both bitstreams always carry the same configuration.  This layout must match
rtl/rtl/pe_cfg.sv and the slicing in rtl/rtl/mocarabe.sv.
"""

import json
import os

from .header_gen import FIFO_DEPTH


def clog2(n):
    return max(1, (n - 1).bit_length())


def frame_fields(C):
    """[(name, width)] from bit 0 up for one PE slot, and the frame width"""
    fields = []
    for c in range(C):
        fields += [(f"north_c{c}", 2), (f"east_c{c}", 2), (f"to_pe_c{c}", 2)]
    addr_w = clog2(FIFO_DEPTH)
    sel_w = clog2(C)
    fields += [("op1_addr", addr_w), ("op2_addr", addr_w), ("mux_sel0", sel_w), ("mux_sel1", sel_w)]
    return fields, sum(width for _, width in fields)


def words_per_frame(frame_w, cfg_width):
    return -(-frame_w // cfg_width)


def read_dat(path, base, length):
    with open(path) as f:
        values = [int(line, base) for line in f.read().split()]
    assert len(values) == length, f"{path}: expected {length} entries, found {len(values)}"
    return values


def pe_slot_values(rtl_dir, x, y, C, II):
    """{field: [value per slot]} for one PE, from the hard bitstream's .dat files"""
    values = {}
    for c in range(C):
        for name, kind in (("north", "n"), ("east", "e"), ("to_pe", "pe")):
            path = os.path.join(rtl_dir, f"noc_memory_{kind}_x{x}_y{y}_c{c}.dat")
            values[f"{name}_c{c}"] = read_dat(path, 2, II)
    for operand in (1, 2):
        path = os.path.join(rtl_dir, f"op{operand}_addr_memory_x{x}_y{y}.dat")
        values[f"op{operand}_addr"] = read_dat(path, 16, II)
    for port in (0, 1):
        path = os.path.join(rtl_dir, f"pe_mux_x{x}_y{y}_sel_mem{port}.dat")
        values[f"mux_sel{port}"] = read_dat(path, 2, II)
    return values


def write_bitstream(rtl_dir, Nx, Ny, C, II, ii_max, cfg_width):
    """Write bitstream.hex and bitstream_layout.json; return the number of words."""
    assert C > 1, "the soft bitstream needs more than one channel"
    assert ii_max >= II, f"II_MAX {ii_max} is smaller than II {II}"
    fields, frame_w = frame_fields(C)
    ii_w = clog2(ii_max)

    frames = [II - 1]  # global row
    for p in range(Nx * Ny):
        x, y = p % Nx, p // Nx
        values = pe_slot_values(rtl_dir, x, y, C, II)
        for t in range(ii_max):
            frame, offset = 0, 0
            for name, width in fields:
                value = values[name][t] if t < II else 0
                assert value < 2**width, f"PE ({x},{y}) slot {t}: {name}={value} needs more than {width} bits"
                frame |= value << offset
                offset += width
            frames.append(frame)

    wpf = words_per_frame(frame_w, cfg_width)
    digits = -(-cfg_width // 4)
    mask = 2**cfg_width - 1
    words = []
    for frame in frames:
        for k in reversed(range(wpf)):  # most significant word first
            words.append((frame >> (k * cfg_width)) & mask)

    with open(os.path.join(rtl_dir, "bitstream.hex"), "w") as f:
        f.write("".join(f"{word:0{digits}x}\n" for word in words))
    with open(os.path.join(rtl_dir, "bitstream_layout.json"), "w") as f:
        json.dump(
            {
                "cfg_width": cfg_width,
                "frame_width": frame_w,
                "words_per_frame": wpf,
                "ii": II,
                "ii_max": ii_max,
                "global_row": {"ii_minus_1": [0, ii_w]},
                "pe_rows": "pe = x + y*Nx, then slot 0..ii_max-1",
                "frame_fields": [[name, width] for name, width in fields],
                "rows": len(frames),
                "words": len(words),
            },
            f,
            indent=2,
        )
    return len(words)


def read_frames(rtl_dir):
    """Inverse of write_bitstream: the frames in bitstream.hex, as integers"""
    with open(os.path.join(rtl_dir, "bitstream_layout.json")) as f:
        layout = json.load(f)
    with open(os.path.join(rtl_dir, "bitstream.hex")) as f:
        words = [int(line, 16) for line in f.read().split()]
    wpf, cfg_width = layout["words_per_frame"], layout["cfg_width"]
    frames = []
    for start in range(0, len(words), wpf):
        frame = 0
        for word in words[start:start + wpf]:
            frame = (frame << cfg_width) | word
        frames.append(frame)
    return frames, layout
