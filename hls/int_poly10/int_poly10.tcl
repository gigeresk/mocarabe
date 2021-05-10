open_project int_poly10
set_top int_poly10

add_files int_poly10.c

open_solution "solution1"
set_part {xcu280-fsvh2892-2L-e}

create_clock -period 4



set_directive_pipeline int_poly10/loop1 -II 5
set_directive_unroll int_poly10/loop1 -factor 1
#set_directive_unroll -factor 1 

# ATTENTION
# -----------------------------------------
# ADD EVERY INPUT AND OUTPUT PARAMETER HERE
# -----------------------------------------
# May not want to unroll right now, but need this
set_directive_array_partition -type cyclic -factor 1 int_poly10 x
set_directive_array_partition -type cyclic -factor 1 int_poly10 c1
set_directive_array_partition -type cyclic -factor 1 int_poly10 c2
set_directive_array_partition -type cyclic -factor 1 int_poly10 c3
set_directive_array_partition -type cyclic -factor 1 int_poly10 c4
set_directive_array_partition -type cyclic -factor 1 int_poly10 c5
set_directive_array_partition -type cyclic -factor 1 int_poly10 c6

set_directive_array_partition -type cyclic -factor 1 int_poly10 y

#Every operator
set_directive_allocation -limit 1 -type operation int_poly10/loop1 add
set_directive_allocation -limit 1 -type operation int_poly10/loop1 fadd
set_directive_allocation -limit 1 -type operation int_poly10/loop1 dadd

set_directive_allocation -limit 1 -type operation int_poly10/loop1 mul
set_directive_allocation -limit 1 -type operation int_poly10/loop1 fmul
set_directive_allocation -limit 1 -type operation int_poly10/loop1 dmul

set_directive_allocation -limit 1 -type operation int_poly10/loop1 sdiv
set_directive_allocation -limit 1 -type operation int_poly10/loop1 fdiv
set_directive_allocation -limit 1 -type operation int_poly10/loop1 ddiv


config_schedule -relax_ii_for_timing=0

csynth_design
#cosim_design -rtl verilog
#export_design
export_design -evaluate verilog -format ip_catalog

exit
