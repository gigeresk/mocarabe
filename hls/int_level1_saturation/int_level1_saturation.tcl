open_project int_level1_saturation
set_top int_level1_saturation

add_files int_level1_saturation.c

open_solution "solution1"
#set_part {xcvu9p-flga2104-2-i-EVAL}
#set_part  {xc7z020clg400-1}
set_part {xcu280-fsvh2892-2L-e}

create_clock -period 4

set_directive_pipeline int_level1_saturation/loop1 -II 5
set_directive_unroll int_level1_saturation/loop1 -factor 1
#set_directive_unroll -factor 1 

# ATTENTION
# -----------------------------------------
# ADD EVERY INPUT AND OUTPUT PARAMETER HERE
# -----------------------------------------
# May not want to unroll right now, but need this
set_directive_array_partition -type cyclic -factor 1 int_level1_saturation x1
set_directive_array_partition -type cyclic -factor 1 int_level1_saturation x2
set_directive_array_partition -type cyclic -factor 1 int_level1_saturation x3
set_directive_array_partition -type cyclic -factor 1 int_level1_saturation c1
set_directive_array_partition -type cyclic -factor 1 int_level1_saturation c2
set_directive_array_partition -type cyclic -factor 1 int_level1_saturation ret

#Every operator
set_directive_allocation -limit 1 -type operation int_level1_saturation/loop1 add
set_directive_allocation -limit 1 -type operation int_level1_saturation/loop1 fadd
set_directive_allocation -limit 1 -type operation int_level1_saturation/loop1 dadd

set_directive_allocation -limit 1 -type operation int_level1_saturation/loop1 mul
set_directive_allocation -limit 1 -type operation int_level1_saturation/loop1 fmul
set_directive_allocation -limit 1 -type operation int_level1_saturation/loop1 dmul

set_directive_allocation -limit 1 -type operation int_level1_saturation/loop1 sdiv
set_directive_allocation -limit 1 -type operation int_level1_saturation/loop1 fdiv
set_directive_allocation -limit 1 -type operation int_level1_saturation/loop1 ddiv


config_schedule -relax_ii_for_timing=0

csynth_design
#cosim_design -rtl verilog
#export_design
export_design -evaluate verilog -format ip_catalog

exit
