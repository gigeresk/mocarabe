open_project int_deriche
set_top int_deriche

add_files int_deriche.c

open_solution "solution1"
set_part {xcu280-fsvh2892-2L-e}

create_clock -period 4



set_directive_pipeline int_deriche/loop1 -II 5
set_directive_unroll int_deriche/loop1 -factor 1
#set_directive_unroll -factor 1 

# ATTENTION
# -----------------------------------------
# ADD EVERY INPUT AND OUTPUT PARAMETER HERE
# -----------------------------------------
# May not want to unroll right now, but need this
set_directive_array_partition -type cyclic -factor 1 int_deriche x1
set_directive_array_partition -type cyclic -factor 1 int_deriche x2
set_directive_array_partition -type cyclic -factor 1 int_deriche x3
set_directive_array_partition -type cyclic -factor 1 int_deriche x4
set_directive_array_partition -type cyclic -factor 1 int_deriche x5
set_directive_array_partition -type cyclic -factor 1 int_deriche x6
set_directive_array_partition -type cyclic -factor 1 int_deriche x7
set_directive_array_partition -type cyclic -factor 1 int_deriche x8

set_directive_array_partition -type cyclic -factor 1 int_deriche y1
set_directive_array_partition -type cyclic -factor 1 int_deriche y2
set_directive_array_partition -type cyclic -factor 1 int_deriche y3
set_directive_array_partition -type cyclic -factor 1 int_deriche y4
set_directive_array_partition -type cyclic -factor 1 int_deriche y5
set_directive_array_partition -type cyclic -factor 1 int_deriche y6
set_directive_array_partition -type cyclic -factor 1 int_deriche y7
set_directive_array_partition -type cyclic -factor 1 int_deriche y8

set_directive_array_partition -type cyclic -factor 1 int_deriche z1
set_directive_array_partition -type cyclic -factor 1 int_deriche z2
set_directive_array_partition -type cyclic -factor 1 int_deriche z3
set_directive_array_partition -type cyclic -factor 1 int_deriche z4
set_directive_array_partition -type cyclic -factor 1 int_deriche z5
set_directive_array_partition -type cyclic -factor 1 int_deriche z6
set_directive_array_partition -type cyclic -factor 1 int_deriche z7
set_directive_array_partition -type cyclic -factor 1 int_deriche z8

set_directive_array_partition -type cyclic -factor 1 int_deriche w1
set_directive_array_partition -type cyclic -factor 1 int_deriche w2
set_directive_array_partition -type cyclic -factor 1 int_deriche w3
set_directive_array_partition -type cyclic -factor 1 int_deriche w4
set_directive_array_partition -type cyclic -factor 1 int_deriche w5
set_directive_array_partition -type cyclic -factor 1 int_deriche w6
set_directive_array_partition -type cyclic -factor 1 int_deriche w7
set_directive_array_partition -type cyclic -factor 1 int_deriche w8

set_directive_array_partition -type cyclic -factor 1 int_deriche a1
set_directive_array_partition -type cyclic -factor 1 int_deriche a2
set_directive_array_partition -type cyclic -factor 1 int_deriche a3
set_directive_array_partition -type cyclic -factor 1 int_deriche a4
set_directive_array_partition -type cyclic -factor 1 int_deriche a5
set_directive_array_partition -type cyclic -factor 1 int_deriche a6
set_directive_array_partition -type cyclic -factor 1 int_deriche a7
set_directive_array_partition -type cyclic -factor 1 int_deriche a8

set_directive_array_partition -type cyclic -factor 1 int_deriche h1
set_directive_array_partition -type cyclic -factor 1 int_deriche h2
set_directive_array_partition -type cyclic -factor 1 int_deriche h3
set_directive_array_partition -type cyclic -factor 1 int_deriche h4

set_directive_array_partition -type cyclic -factor 1 int_deriche c1
set_directive_array_partition -type cyclic -factor 1 int_deriche c2

set_directive_array_partition -type cyclic -factor 1 int_deriche b1
set_directive_array_partition -type cyclic -factor 1 int_deriche b2

set_directive_array_partition -type cyclic -factor 1 int_deriche sum

#Every operator
set_directive_allocation -limit 1 -type operation int_deriche/loop1 add
set_directive_allocation -limit 1 -type operation int_deriche/loop1 fadd
set_directive_allocation -limit 1 -type operation int_deriche/loop1 dadd

set_directive_allocation -limit 1 -type operation int_deriche/loop1 mul
set_directive_allocation -limit 1 -type operation int_deriche/loop1 fmul
set_directive_allocation -limit 1 -type operation int_deriche/loop1 dmul

set_directive_allocation -limit 1 -type operation int_deriche/loop1 sdiv
set_directive_allocation -limit 1 -type operation int_deriche/loop1 fdiv
set_directive_allocation -limit 1 -type operation int_deriche/loop1 ddiv


config_schedule -relax_ii_for_timing=0

csynth_design
#cosim_design -rtl verilog
#export_design
export_design -evaluate verilog -format ip_catalog

exit
