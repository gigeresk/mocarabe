open_project int_fig3
set_top int_fig3

add_files int_fig3.c

open_solution "solution1"
#set_part {xcvu9p-flga2104-2-i-EVAL}
#set_part  {xc7z020clg400-1}
set_part {xcu280-fsvh2892-2L-e}

create_clock -period 4

set_directive_pipeline int_fig3/loop1 -II 5
set_directive_unroll int_fig3/loop1 -factor 1
#set_directive_unroll -factor 1 

# ATTENTION
# -----------------------------------------
# ADD EVERY INPUT AND OUTPUT PARAMETER HERE
# -----------------------------------------
# May not want to unroll right now, but need this
set_directive_array_partition -type cyclic -factor 1 int_fig3 a
set_directive_array_partition -type cyclic -factor 1 int_fig3 b
set_directive_array_partition -type cyclic -factor 1 int_fig3 c
set_directive_array_partition -type cyclic -factor 1 int_fig3 ret

#Every operator
set_directive_allocation -limit 1 -type operation int_fig3/loop1 add
set_directive_allocation -limit 1 -type operation int_fig3/loop1 fadd
set_directive_allocation -limit 1 -type operation int_fig3/loop1 dadd

set_directive_allocation -limit 1 -type operation int_fig3/loop1 mul
set_directive_allocation -limit 1 -type operation int_fig3/loop1 fmul
set_directive_allocation -limit 1 -type operation int_fig3/loop1 dmul

set_directive_allocation -limit 1 -type operation int_fig3/loop1 sdiv
set_directive_allocation -limit 1 -type operation int_fig3/loop1 fdiv
set_directive_allocation -limit 1 -type operation int_fig3/loop1 ddiv


config_schedule -relax_ii_for_timing=0

csynth_design
#cosim_design -rtl verilog
#export_design
export_design -evaluate verilog -format ip_catalog

exit
