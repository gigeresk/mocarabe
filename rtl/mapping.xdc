create_clock -period 1.000 -name clk -waveform {0.000 0.500 } [get_ports clk]


#col number 0
create_pblock y0x0
add_cells_to_pblock [get_pblocks y0x0] [get_cells -quiet [list {ys[0].xs[0].cs[0].torus_switch_inst} {ys[0].xs[0].pe_inst}]]
add_cells_to_pblock [get_pblocks y0x0] [get_cells -quiet [list {ys[0].xs[0].mux_inst}]]
add_cells_to_pblock [get_pblocks y0x0] [get_cells -quiet [list {ys[0].xs[0].cs[1].torus_switch_inst}]]
add_cells_to_pblock [get_pblocks y0x0] [get_cells -quiet [list {ys[0].xs[0].cs[2].torus_switch_inst}]]
resize_pblock [get_pblocks y0x0] -add {SLICE_X16Y20:SLICE_X25Y29}
set_property gridtypes {DSP48E2 SLICE} [get_pblocks y0x0]
add_cells_to_pblock [get_pblocks y0x0] [get_cells ys[0].xs[0].pe_inst/* -filter {REF_NAME == DSP48E2}]

create_pblock y2x0
add_cells_to_pblock [get_pblocks y2x0] [get_cells -quiet [list {ys[2].xs[0].cs[0].torus_switch_inst} {ys[2].xs[0].pe_inst}]]
add_cells_to_pblock [get_pblocks y2x0] [get_cells -quiet [list {ys[2].xs[0].mux_inst}]]
add_cells_to_pblock [get_pblocks y2x0] [get_cells -quiet [list {ys[2].xs[0].cs[1].torus_switch_inst}]]
add_cells_to_pblock [get_pblocks y2x0] [get_cells -quiet [list {ys[2].xs[0].cs[2].torus_switch_inst}]]
resize_pblock [get_pblocks y2x0] -add {SLICE_X16Y30:SLICE_X25Y39}
set_property gridtypes {DSP48E2 SLICE} [get_pblocks y2x0]
add_cells_to_pblock [get_pblocks y2x0] [get_cells ys[2].xs[0].pe_inst/* -filter {REF_NAME == DSP48E2}]

create_pblock y1x0
add_cells_to_pblock [get_pblocks y1x0] [get_cells -quiet [list {ys[1].xs[0].cs[0].torus_switch_inst} {ys[1].xs[0].pe_inst}]]
add_cells_to_pblock [get_pblocks y1x0] [get_cells -quiet [list {ys[1].xs[0].mux_inst}]]
add_cells_to_pblock [get_pblocks y1x0] [get_cells -quiet [list {ys[1].xs[0].cs[1].torus_switch_inst}]]
add_cells_to_pblock [get_pblocks y1x0] [get_cells -quiet [list {ys[1].xs[0].cs[2].torus_switch_inst}]]
resize_pblock [get_pblocks y1x0] -add {SLICE_X16Y40:SLICE_X25Y49}
set_property gridtypes {DSP48E2 SLICE} [get_pblocks y1x0]
add_cells_to_pblock [get_pblocks y1x0] [get_cells ys[1].xs[0].pe_inst/* -filter {REF_NAME == DSP48E2}]



#col number 1
create_pblock y0x2
add_cells_to_pblock [get_pblocks y0x2] [get_cells -quiet [list {ys[0].xs[2].cs[0].torus_switch_inst} {ys[0].xs[2].pe_inst}]]
add_cells_to_pblock [get_pblocks y0x2] [get_cells -quiet [list {ys[0].xs[2].mux_inst}]]
add_cells_to_pblock [get_pblocks y0x2] [get_cells -quiet [list {ys[0].xs[2].cs[1].torus_switch_inst}]]
add_cells_to_pblock [get_pblocks y0x2] [get_cells -quiet [list {ys[0].xs[2].cs[2].torus_switch_inst}]]
resize_pblock [get_pblocks y0x2] -add {SLICE_X26Y20:SLICE_X35Y29}
set_property gridtypes {DSP48E2 SLICE} [get_pblocks y0x2]
add_cells_to_pblock [get_pblocks y0x2] [get_cells ys[0].xs[2].pe_inst/* -filter {REF_NAME == DSP48E2}]

create_pblock y2x2
add_cells_to_pblock [get_pblocks y2x2] [get_cells -quiet [list {ys[2].xs[2].cs[0].torus_switch_inst} {ys[2].xs[2].pe_inst}]]
add_cells_to_pblock [get_pblocks y2x2] [get_cells -quiet [list {ys[2].xs[2].mux_inst}]]
add_cells_to_pblock [get_pblocks y2x2] [get_cells -quiet [list {ys[2].xs[2].cs[1].torus_switch_inst}]]
add_cells_to_pblock [get_pblocks y2x2] [get_cells -quiet [list {ys[2].xs[2].cs[2].torus_switch_inst}]]
resize_pblock [get_pblocks y2x2] -add {SLICE_X26Y30:SLICE_X35Y39}
set_property gridtypes {DSP48E2 SLICE} [get_pblocks y2x2]
add_cells_to_pblock [get_pblocks y2x2] [get_cells ys[2].xs[2].pe_inst/* -filter {REF_NAME == DSP48E2}]

create_pblock y1x2
add_cells_to_pblock [get_pblocks y1x2] [get_cells -quiet [list {ys[1].xs[2].cs[0].torus_switch_inst} {ys[1].xs[2].pe_inst}]]
add_cells_to_pblock [get_pblocks y1x2] [get_cells -quiet [list {ys[1].xs[2].mux_inst}]]
add_cells_to_pblock [get_pblocks y1x2] [get_cells -quiet [list {ys[1].xs[2].cs[1].torus_switch_inst}]]
add_cells_to_pblock [get_pblocks y1x2] [get_cells -quiet [list {ys[1].xs[2].cs[2].torus_switch_inst}]]
resize_pblock [get_pblocks y1x2] -add {SLICE_X26Y40:SLICE_X35Y49}
set_property gridtypes {DSP48E2 SLICE} [get_pblocks y1x2]
add_cells_to_pblock [get_pblocks y1x2] [get_cells ys[1].xs[2].pe_inst/* -filter {REF_NAME == DSP48E2}]



#col number 2
create_pblock y0x1
add_cells_to_pblock [get_pblocks y0x1] [get_cells -quiet [list {ys[0].xs[1].cs[0].torus_switch_inst} {ys[0].xs[1].pe_inst}]]
add_cells_to_pblock [get_pblocks y0x1] [get_cells -quiet [list {ys[0].xs[1].mux_inst}]]
add_cells_to_pblock [get_pblocks y0x1] [get_cells -quiet [list {ys[0].xs[1].cs[1].torus_switch_inst}]]
add_cells_to_pblock [get_pblocks y0x1] [get_cells -quiet [list {ys[0].xs[1].cs[2].torus_switch_inst}]]
resize_pblock [get_pblocks y0x1] -add {SLICE_X36Y20:SLICE_X45Y29}
set_property gridtypes {DSP48E2 SLICE} [get_pblocks y0x1]
add_cells_to_pblock [get_pblocks y0x1] [get_cells ys[0].xs[1].pe_inst/* -filter {REF_NAME == DSP48E2}]

create_pblock y2x1
add_cells_to_pblock [get_pblocks y2x1] [get_cells -quiet [list {ys[2].xs[1].cs[0].torus_switch_inst} {ys[2].xs[1].pe_inst}]]
add_cells_to_pblock [get_pblocks y2x1] [get_cells -quiet [list {ys[2].xs[1].mux_inst}]]
add_cells_to_pblock [get_pblocks y2x1] [get_cells -quiet [list {ys[2].xs[1].cs[1].torus_switch_inst}]]
add_cells_to_pblock [get_pblocks y2x1] [get_cells -quiet [list {ys[2].xs[1].cs[2].torus_switch_inst}]]
resize_pblock [get_pblocks y2x1] -add {SLICE_X36Y30:SLICE_X45Y39}
set_property gridtypes {DSP48E2 SLICE} [get_pblocks y2x1]
add_cells_to_pblock [get_pblocks y2x1] [get_cells ys[2].xs[1].pe_inst/* -filter {REF_NAME == DSP48E2}]

create_pblock y1x1
add_cells_to_pblock [get_pblocks y1x1] [get_cells -quiet [list {ys[1].xs[1].cs[0].torus_switch_inst} {ys[1].xs[1].pe_inst}]]
add_cells_to_pblock [get_pblocks y1x1] [get_cells -quiet [list {ys[1].xs[1].mux_inst}]]
add_cells_to_pblock [get_pblocks y1x1] [get_cells -quiet [list {ys[1].xs[1].cs[1].torus_switch_inst}]]
add_cells_to_pblock [get_pblocks y1x1] [get_cells -quiet [list {ys[1].xs[1].cs[2].torus_switch_inst}]]
resize_pblock [get_pblocks y1x1] -add {SLICE_X36Y40:SLICE_X45Y49}
set_property gridtypes {DSP48E2 SLICE} [get_pblocks y1x1]
add_cells_to_pblock [get_pblocks y1x1] [get_cells ys[1].xs[1].pe_inst/* -filter {REF_NAME == DSP48E2}]



