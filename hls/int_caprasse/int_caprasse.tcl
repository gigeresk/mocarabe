open_project int_caprasse
set_top int_caprasse

add_files int_caprasse.c

open_solution "solution1"
#set_part {xcvu9p-flga2104-2-i-EVAL}
#set_part  {xc7z020clg400-1}
set_part {xcu280-fsvh2892-2L-e}

create_clock -period 4

set_directive_pipeline int_caprasse/loop1 -II 4
set_directive_unroll int_caprasse/loop1 -factor 1
#set_directive_unroll -factor 1 

# ATTENTION
# -----------------------------------------
# ADD EVERY INPUT AND OUTPUT PARAMETER HERE
# -----------------------------------------
# May not want to unroll right now, but need this
set_directive_array_partition -type cyclic -factor 1 int_caprasse x
set_directive_array_partition -type cyclic -factor 1 int_caprasse y
set_directive_array_partition -type cyclic -factor 1 int_caprasse z
set_directive_array_partition -type cyclic -factor 1 int_caprasse t
set_directive_array_partition -type cyclic -factor 1 int_caprasse ret

#Every operator
set_directive_allocation -limit 1 -type operation int_caprasse/loop1 add
set_directive_allocation -limit 1 -type operation int_caprasse/loop1 fadd
set_directive_allocation -limit 1 -type operation int_caprasse/loop1 dadd

set_directive_allocation -limit 1 -type operation int_caprasse/loop1 mul
set_directive_allocation -limit 1 -type operation int_caprasse/loop1 fmul
set_directive_allocation -limit 1 -type operation int_caprasse/loop1 dmul

set_directive_allocation -limit 1 -type operation int_caprasse/loop1 sdiv
set_directive_allocation -limit 1 -type operation int_caprasse/loop1 fdiv
set_directive_allocation -limit 1 -type operation int_caprasse/loop1 ddiv

config_schedule -relax_ii_for_timing=0


csynth_design
#cosim_design -rtl verilog
#export_design
export_design -evaluate verilog -format ip_catalog

exit
