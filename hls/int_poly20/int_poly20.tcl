open_project int_poly20
set_top int_poly20

add_files int_poly20.c

open_solution "solution1"
set_part {xcu280-fsvh2892-2L-e}

create_clock -period 4



set_directive_pipeline int_poly20/loop1 -II 5
set_directive_unroll int_poly20/loop1 -factor 1
#set_directive_unroll -factor 1 

# ATTENTION
# -----------------------------------------
# ADD EVERY INPUT AND OUTPUT PARAMETER HERE
# -----------------------------------------
# May not want to unroll right now, but need this
set_directive_array_partition -type cyclic -factor 1 int_poly20 x
set_directive_array_partition -type cyclic -factor 1 int_poly20 c1
set_directive_array_partition -type cyclic -factor 1 int_poly20 c2
set_directive_array_partition -type cyclic -factor 1 int_poly20 c3
set_directive_array_partition -type cyclic -factor 1 int_poly20 c4
set_directive_array_partition -type cyclic -factor 1 int_poly20 c5
set_directive_array_partition -type cyclic -factor 1 int_poly20 c6
set_directive_array_partition -type cyclic -factor 1 int_poly20 c7
set_directive_array_partition -type cyclic -factor 1 int_poly20 c8
set_directive_array_partition -type cyclic -factor 1 int_poly20 c9
set_directive_array_partition -type cyclic -factor 1 int_poly20 a0
set_directive_array_partition -type cyclic -factor 1 int_poly20 a1
set_directive_array_partition -type cyclic -factor 1 int_poly20 a2
set_directive_array_partition -type cyclic -factor 1 int_poly20 a3
set_directive_array_partition -type cyclic -factor 1 int_poly20 a4
set_directive_array_partition -type cyclic -factor 1 int_poly20 a5
set_directive_array_partition -type cyclic -factor 1 int_poly20 a6
set_directive_array_partition -type cyclic -factor 1 int_poly20 a7
set_directive_array_partition -type cyclic -factor 1 int_poly20 a8
set_directive_array_partition -type cyclic -factor 1 int_poly20 a9
set_directive_array_partition -type cyclic -factor 1 int_poly20 y


#Every operator
set_directive_allocation -limit 1 -type operation int_poly20/loop1 add
set_directive_allocation -limit 1 -type operation int_poly20/loop1 fadd
set_directive_allocation -limit 1 -type operation int_poly20/loop1 dadd

set_directive_allocation -limit 1 -type operation int_poly20/loop1 mul
set_directive_allocation -limit 1 -type operation int_poly20/loop1 fmul
set_directive_allocation -limit 1 -type operation int_poly20/loop1 dmul

set_directive_allocation -limit 1 -type operation int_poly20/loop1 sdiv
set_directive_allocation -limit 1 -type operation int_poly20/loop1 fdiv
set_directive_allocation -limit 1 -type operation int_poly20/loop1 ddiv


config_schedule -relax_ii_for_timing=0

csynth_design
#cosim_design -rtl verilog
#export_design
export_design -evaluate verilog -format ip_catalog

exit
