open_project int_iir8
set_top int_iir8

add_files int_iir8.c

open_solution "solution1"
#set_part {xcvu9p-flga2104-2-i-EVAL}
#set_part  {xc7z020clg400-1}
set_part {xcu280-fsvh2892-2L-e}

create_clock -period 4

set_directive_pipeline int_iir8/loop1 -II 5
set_directive_unroll int_iir8/loop1 -factor 1
#set_directive_unroll -factor 1 

# ATTENTION
# -----------------------------------------
# ADD EVERY INPUT AND OUTPUT PARAMETER HERE
# -----------------------------------------
# May not want to unroll right now, but need this
set_directive_array_partition -type cyclic -factor 1 int_iir8 a0
set_directive_array_partition -type cyclic -factor 1 int_iir8 a1
set_directive_array_partition -type cyclic -factor 1 int_iir8 a2
set_directive_array_partition -type cyclic -factor 1 int_iir8 a3
set_directive_array_partition -type cyclic -factor 1 int_iir8 a4
set_directive_array_partition -type cyclic -factor 1 int_iir8 a5
set_directive_array_partition -type cyclic -factor 1 int_iir8 a6
set_directive_array_partition -type cyclic -factor 1 int_iir8 a7

set_directive_array_partition -type cyclic -factor 1 int_iir8 b0
set_directive_array_partition -type cyclic -factor 1 int_iir8 b1
set_directive_array_partition -type cyclic -factor 1 int_iir8 b2
set_directive_array_partition -type cyclic -factor 1 int_iir8 b3
set_directive_array_partition -type cyclic -factor 1 int_iir8 b4
set_directive_array_partition -type cyclic -factor 1 int_iir8 b5
set_directive_array_partition -type cyclic -factor 1 int_iir8 b6

set_directive_array_partition -type cyclic -factor 1 int_iir8 x0
set_directive_array_partition -type cyclic -factor 1 int_iir8 x1
set_directive_array_partition -type cyclic -factor 1 int_iir8 x2
set_directive_array_partition -type cyclic -factor 1 int_iir8 x3
set_directive_array_partition -type cyclic -factor 1 int_iir8 x4
set_directive_array_partition -type cyclic -factor 1 int_iir8 x5
set_directive_array_partition -type cyclic -factor 1 int_iir8 x6
set_directive_array_partition -type cyclic -factor 1 int_iir8 x7

set_directive_array_partition -type cyclic -factor 1 int_iir8 y0
set_directive_array_partition -type cyclic -factor 1 int_iir8 y1
set_directive_array_partition -type cyclic -factor 1 int_iir8 y2
set_directive_array_partition -type cyclic -factor 1 int_iir8 y3
set_directive_array_partition -type cyclic -factor 1 int_iir8 y4
set_directive_array_partition -type cyclic -factor 1 int_iir8 y5
set_directive_array_partition -type cyclic -factor 1 int_iir8 y6
set_directive_array_partition -type cyclic -factor 1 int_iir8 y7


#Every operator
set_directive_allocation -limit 1 -type operation int_iir8/loop1 add
set_directive_allocation -limit 1 -type operation int_iir8/loop1 fadd
set_directive_allocation -limit 1 -type operation int_iir8/loop1 dadd

set_directive_allocation -limit 1 -type operation int_iir8/loop1 mul
set_directive_allocation -limit 1 -type operation int_iir8/loop1 fmul
set_directive_allocation -limit 1 -type operation int_iir8/loop1 dmul

set_directive_allocation -limit 1 -type operation int_iir8/loop1 sdiv
set_directive_allocation -limit 1 -type operation int_iir8/loop1 fdiv
set_directive_allocation -limit 1 -type operation int_iir8/loop1 ddiv


config_schedule -relax_ii_for_timing=0

csynth_design
#cosim_design -rtl verilog
#export_design
export_design -evaluate verilog -format ip_catalog

exit
