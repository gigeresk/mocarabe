open_project int_fir32
set_top int_fir32

add_files int_fir32.c

open_solution "solution1"
set_part {xcu280-fsvh2892-2L-e}

create_clock -period 4



set_directive_pipeline int_fir32/loop1 -II 1
set_directive_unroll int_fir32/loop1 -factor 1
#set_directive_unroll -factor 1 

# ATTENTION
# -----------------------------------------
# ADD EVERY INPUT AND OUTPUT PARAMETER HERE
# -----------------------------------------
# May not want to unroll right now, but need this
set_directive_array_partition -type cyclic -factor 1 int_fir32 x0
set_directive_array_partition -type cyclic -factor 1 int_fir32 x1
set_directive_array_partition -type cyclic -factor 1 int_fir32 x2
set_directive_array_partition -type cyclic -factor 1 int_fir32 x3
set_directive_array_partition -type cyclic -factor 1 int_fir32 x4
set_directive_array_partition -type cyclic -factor 1 int_fir32 x5
set_directive_array_partition -type cyclic -factor 1 int_fir32 x6
set_directive_array_partition -type cyclic -factor 1 int_fir32 x7
set_directive_array_partition -type cyclic -factor 1 int_fir32 x8
set_directive_array_partition -type cyclic -factor 1 int_fir32 x9

set_directive_array_partition -type cyclic -factor 1 int_fir32 y0
set_directive_array_partition -type cyclic -factor 1 int_fir32 y1
set_directive_array_partition -type cyclic -factor 1 int_fir32 y2
set_directive_array_partition -type cyclic -factor 1 int_fir32 y3
set_directive_array_partition -type cyclic -factor 1 int_fir32 y4
set_directive_array_partition -type cyclic -factor 1 int_fir32 y5
set_directive_array_partition -type cyclic -factor 1 int_fir32 y6
set_directive_array_partition -type cyclic -factor 1 int_fir32 y7
set_directive_array_partition -type cyclic -factor 1 int_fir32 y8
set_directive_array_partition -type cyclic -factor 1 int_fir32 y9

set_directive_array_partition -type cyclic -factor 1 int_fir32 z0
set_directive_array_partition -type cyclic -factor 1 int_fir32 z1
set_directive_array_partition -type cyclic -factor 1 int_fir32 z2
set_directive_array_partition -type cyclic -factor 1 int_fir32 z3
set_directive_array_partition -type cyclic -factor 1 int_fir32 z4
set_directive_array_partition -type cyclic -factor 1 int_fir32 z5
set_directive_array_partition -type cyclic -factor 1 int_fir32 z6
set_directive_array_partition -type cyclic -factor 1 int_fir32 z7
set_directive_array_partition -type cyclic -factor 1 int_fir32 z8
set_directive_array_partition -type cyclic -factor 1 int_fir32 z9

set_directive_array_partition -type cyclic -factor 1 int_fir32 a0
set_directive_array_partition -type cyclic -factor 1 int_fir32 a1
set_directive_array_partition -type cyclic -factor 1 int_fir32 a2
set_directive_array_partition -type cyclic -factor 1 int_fir32 a3
set_directive_array_partition -type cyclic -factor 1 int_fir32 a4
set_directive_array_partition -type cyclic -factor 1 int_fir32 a5
set_directive_array_partition -type cyclic -factor 1 int_fir32 a6
set_directive_array_partition -type cyclic -factor 1 int_fir32 a7
set_directive_array_partition -type cyclic -factor 1 int_fir32 a8
set_directive_array_partition -type cyclic -factor 1 int_fir32 a9

set_directive_array_partition -type cyclic -factor 1 int_fir32 b0
set_directive_array_partition -type cyclic -factor 1 int_fir32 b1
set_directive_array_partition -type cyclic -factor 1 int_fir32 b2
set_directive_array_partition -type cyclic -factor 1 int_fir32 b3
set_directive_array_partition -type cyclic -factor 1 int_fir32 b4
set_directive_array_partition -type cyclic -factor 1 int_fir32 b5
set_directive_array_partition -type cyclic -factor 1 int_fir32 b6
set_directive_array_partition -type cyclic -factor 1 int_fir32 b7
set_directive_array_partition -type cyclic -factor 1 int_fir32 b8
set_directive_array_partition -type cyclic -factor 1 int_fir32 b9

set_directive_array_partition -type cyclic -factor 1 int_fir32 c0
set_directive_array_partition -type cyclic -factor 1 int_fir32 c1
set_directive_array_partition -type cyclic -factor 1 int_fir32 c2
set_directive_array_partition -type cyclic -factor 1 int_fir32 c3
set_directive_array_partition -type cyclic -factor 1 int_fir32 c4
set_directive_array_partition -type cyclic -factor 1 int_fir32 c5
set_directive_array_partition -type cyclic -factor 1 int_fir32 c6
set_directive_array_partition -type cyclic -factor 1 int_fir32 c7
set_directive_array_partition -type cyclic -factor 1 int_fir32 c8
set_directive_array_partition -type cyclic -factor 1 int_fir32 c9

set_directive_array_partition -type cyclic -factor 1 int_fir32 w0
set_directive_array_partition -type cyclic -factor 1 int_fir32 w1
set_directive_array_partition -type cyclic -factor 1 int_fir32 w2

set_directive_array_partition -type cyclic -factor 1 int_fir32 d0
set_directive_array_partition -type cyclic -factor 1 int_fir32 d1
set_directive_array_partition -type cyclic -factor 1 int_fir32 d2

set_directive_array_partition -type cyclic -factor 1 int_fir32 ret



#Every operator
set_directive_allocation -limit 1 -type operation int_fir32/loop1 add
set_directive_allocation -limit 1 -type operation int_fir32/loop1 fadd
set_directive_allocation -limit 1 -type operation int_fir32/loop1 dadd

set_directive_allocation -limit 1 -type operation int_fir32/loop1 mul
set_directive_allocation -limit 1 -type operation int_fir32/loop1 fmul
set_directive_allocation -limit 1 -type operation int_fir32/loop1 dmul

set_directive_allocation -limit 1 -type operation int_fir32/loop1 sdiv
set_directive_allocation -limit 1 -type operation int_fir32/loop1 fdiv
set_directive_allocation -limit 1 -type operation int_fir32/loop1 ddiv


config_schedule -relax_ii_for_timing=0

csynth_design
#cosim_design -rtl verilog
#export_design
export_design -evaluate verilog -format ip_catalog

exit
