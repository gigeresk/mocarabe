open_project int_rgb
set_top int_rgb

add_files int_rgb.c

open_solution "solution1"
set_part {xcu280-fsvh2892-2L-e}

create_clock -period 4



set_directive_pipeline int_rgb/loop1 -II 5
set_directive_unroll int_rgb/loop1 -factor 1
#set_directive_unroll -factor 1 

# ATTENTION
# -----------------------------------------
# ADD EVERY INPUT AND OUTPUT PARAMETER HERE
# -----------------------------------------
# May not want to unroll right now, but need this
set_directive_array_partition -type cyclic -factor 1 int_rgb R
set_directive_array_partition -type cyclic -factor 1 int_rgb G	
set_directive_array_partition -type cyclic -factor 1 int_rgb B
set_directive_array_partition -type cyclic -factor 1 int_rgb c1
set_directive_array_partition -type cyclic -factor 1 int_rgb c2
set_directive_array_partition -type cyclic -factor 1 int_rgb c3
set_directive_array_partition -type cyclic -factor 1 int_rgb c4
set_directive_array_partition -type cyclic -factor 1 int_rgb c5
set_directive_array_partition -type cyclic -factor 1 int_rgb c6
set_directive_array_partition -type cyclic -factor 1 int_rgb c7
set_directive_array_partition -type cyclic -factor 1 int_rgb c8
set_directive_array_partition -type cyclic -factor 1 int_rgb c9
set_directive_array_partition -type cyclic -factor 1 int_rgb Y
set_directive_array_partition -type cyclic -factor 1 int_rgb Cb
set_directive_array_partition -type cyclic -factor 1 int_rgb Cr


#Every operator
set_directive_allocation -limit 1 -type operation int_rgb/loop1 add
set_directive_allocation -limit 1 -type operation int_rgb/loop1 fadd
set_directive_allocation -limit 1 -type operation int_rgb/loop1 dadd

set_directive_allocation -limit 1 -type operation int_rgb/loop1 mul
set_directive_allocation -limit 1 -type operation int_rgb/loop1 fmul
set_directive_allocation -limit 1 -type operation int_rgb/loop1 dmul

set_directive_allocation -limit 1 -type operation int_rgb/loop1 sdiv
set_directive_allocation -limit 1 -type operation int_rgb/loop1 fdiv
set_directive_allocation -limit 1 -type operation int_rgb/loop1 ddiv



config_schedule -relax_ii_for_timing=0
csynth_design
#cosim_design -rtl verilog
#export_design
export_design -evaluate verilog -format ip_catalog

exit
