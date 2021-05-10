open_project int_dct
set_top int_dct

add_files int_dct.c

open_solution "solution1"
#set_part {xcvu9p-flga2104-2-i-EVAL}
#set_part  {xc7z020clg400-1}
set_part {xcu280-fsvh2892-2L-e}

create_clock -period 4

set_directive_pipeline int_dct/loop1 -II 5
set_directive_unroll int_dct/loop1 -factor 1
#set_directive_unroll -factor 1 

# ATTENTION
# -----------------------------------------
# ADD EVERY INPUT AND OUTPUT PARAMETER HERE
# -----------------------------------------
# May not want to unroll right now, but need this
set_directive_array_partition -type cyclic -factor 1 int_dct x0
set_directive_array_partition -type cyclic -factor 1 int_dct x1
set_directive_array_partition -type cyclic -factor 1 int_dct x2
set_directive_array_partition -type cyclic -factor 1 int_dct x3
set_directive_array_partition -type cyclic -factor 1 int_dct x4
set_directive_array_partition -type cyclic -factor 1 int_dct x5
set_directive_array_partition -type cyclic -factor 1 int_dct x6
set_directive_array_partition -type cyclic -factor 1 int_dct x7

set_directive_array_partition -type cyclic -factor 1 int_dct y0
set_directive_array_partition -type cyclic -factor 1 int_dct y1
set_directive_array_partition -type cyclic -factor 1 int_dct y2
set_directive_array_partition -type cyclic -factor 1 int_dct y3
set_directive_array_partition -type cyclic -factor 1 int_dct y4
set_directive_array_partition -type cyclic -factor 1 int_dct y5
set_directive_array_partition -type cyclic -factor 1 int_dct y6
set_directive_array_partition -type cyclic -factor 1 int_dct y7

set_directive_array_partition -type cyclic -factor 1 int_dct a
set_directive_array_partition -type cyclic -factor 1 int_dct b
set_directive_array_partition -type cyclic -factor 1 int_dct c
set_directive_array_partition -type cyclic -factor 1 int_dct d
set_directive_array_partition -type cyclic -factor 1 int_dct e
set_directive_array_partition -type cyclic -factor 1 int_dct f
set_directive_array_partition -type cyclic -factor 1 int_dct g



#Every operator
set_directive_allocation -limit 1 -type operation int_dct/loop1 add
set_directive_allocation -limit 1 -type operation int_dct/loop1 fadd
set_directive_allocation -limit 1 -type operation int_dct/loop1 dadd

set_directive_allocation -limit 1 -type operation int_dct/loop1 mul
set_directive_allocation -limit 1 -type operation int_dct/loop1 fmul
set_directive_allocation -limit 1 -type operation int_dct/loop1 dmul

set_directive_allocation -limit 1 -type operation int_dct/loop1 sdiv
set_directive_allocation -limit 1 -type operation int_dct/loop1 fdiv
set_directive_allocation -limit 1 -type operation int_dct/loop1 ddiv



config_schedule -relax_ii_for_timing=0
csynth_design
#cosim_design -rtl verilog
#export_design
export_design -evaluate verilog -format ip_catalog

exit

