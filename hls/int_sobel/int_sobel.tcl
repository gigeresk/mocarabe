open_project int_sobel
set_top int_sobel

add_files int_sobel.c

open_solution "solution1"
set_part {xcu280-fsvh2892-2L-e}

create_clock -period 4



set_directive_pipeline int_sobel/loop1 -II 5
set_directive_unroll int_sobel/loop1 -factor 1
#set_directive_unroll -factor 1 

# ATTENTION
# -----------------------------------------
# ADD EVERY INPUT AND OUTPUT PARAMETER HERE
# -----------------------------------------
# May not want to unroll right now, but need this
set_directive_array_partition -type cyclic -factor 1 int_sobel ul
set_directive_array_partition -type cyclic -factor 1 int_sobel um
set_directive_array_partition -type cyclic -factor 1 int_sobel ur
set_directive_array_partition -type cyclic -factor 1 int_sobel ml
set_directive_array_partition -type cyclic -factor 1 int_sobel mr
set_directive_array_partition -type cyclic -factor 1 int_sobel ll
set_directive_array_partition -type cyclic -factor 1 int_sobel lm
set_directive_array_partition -type cyclic -factor 1 int_sobel lr
set_directive_array_partition -type cyclic -factor 1 int_sobel fscale
set_directive_array_partition -type cyclic -factor 1 int_sobel result


#Every operator
set_directive_allocation -limit 1 -type operation int_sobel/loop1 add
set_directive_allocation -limit 1 -type operation int_sobel/loop1 fadd
set_directive_allocation -limit 1 -type operation int_sobel/loop1 dadd

set_directive_allocation -limit 1 -type operation int_sobel/loop1 mul
set_directive_allocation -limit 1 -type operation int_sobel/loop1 fmul
set_directive_allocation -limit 1 -type operation int_sobel/loop1 dmul

set_directive_allocation -limit 1 -type operation int_sobel/loop1 sdiv
set_directive_allocation -limit 1 -type operation int_sobel/loop1 fdiv
set_directive_allocation -limit 1 -type operation int_sobel/loop1 ddiv


config_schedule -relax_ii_for_timing=0

csynth_design
#cosim_design -rtl verilog
#export_design
export_design -evaluate verilog -format ip_catalog

exit
