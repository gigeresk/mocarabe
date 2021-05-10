open_project int_gaussian
set_top int_gaussian

add_files int_gaussian.c

open_solution "solution1"
#set_part {xcvu9p-flga2104-2-i-EVAL}
#set_part  {xc7z020clg400-1}
set_part {xcu280-fsvh2892-2L-e}

create_clock -period 4

set_directive_pipeline int_gaussian/loop1 -II 5
set_directive_unroll int_gaussian/loop1 -factor 1
#set_directive_unroll -factor 1 

# ATTENTION
# -----------------------------------------
# ADD EVERY INPUT AND OUTPUT PARAMETER HERE
# -----------------------------------------
# May not want to unroll right now, but need this
set_directive_array_partition -type cyclic -factor 1 int_gaussian c0
set_directive_array_partition -type cyclic -factor 1 int_gaussian c1
set_directive_array_partition -type cyclic -factor 1 int_gaussian c2
set_directive_array_partition -type cyclic -factor 1 int_gaussian c3
set_directive_array_partition -type cyclic -factor 1 int_gaussian c4
set_directive_array_partition -type cyclic -factor 1 int_gaussian c5
set_directive_array_partition -type cyclic -factor 1 int_gaussian c6
set_directive_array_partition -type cyclic -factor 1 int_gaussian c7
set_directive_array_partition -type cyclic -factor 1 int_gaussian c8

set_directive_array_partition -type cyclic -factor 1 int_gaussian r0
set_directive_array_partition -type cyclic -factor 1 int_gaussian r1
set_directive_array_partition -type cyclic -factor 1 int_gaussian r2
set_directive_array_partition -type cyclic -factor 1 int_gaussian r3
set_directive_array_partition -type cyclic -factor 1 int_gaussian r4
set_directive_array_partition -type cyclic -factor 1 int_gaussian r5
set_directive_array_partition -type cyclic -factor 1 int_gaussian r6
set_directive_array_partition -type cyclic -factor 1 int_gaussian r7
set_directive_array_partition -type cyclic -factor 1 int_gaussian r8

set_directive_array_partition -type cyclic -factor 1 int_gaussian sum

#Every operator
set_directive_allocation -limit 1 -type operation int_gaussian/loop1 add
set_directive_allocation -limit 1 -type operation int_gaussian/loop1 fadd
set_directive_allocation -limit 1 -type operation int_gaussian/loop1 dadd

set_directive_allocation -limit 1 -type operation int_gaussian/loop1 mul
set_directive_allocation -limit 1 -type operation int_gaussian/loop1 fmul
set_directive_allocation -limit 1 -type operation int_gaussian/loop1 dmul

set_directive_allocation -limit 1 -type operation int_gaussian/loop1 sdiv
set_directive_allocation -limit 1 -type operation int_gaussian/loop1 fdiv
set_directive_allocation -limit 1 -type operation int_gaussian/loop1 ddiv


config_schedule -relax_ii_for_timing=0

csynth_design
#cosim_design -rtl verilog
#export_design
export_design -evaluate verilog -format ip_catalog

exit
