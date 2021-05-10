open_project int_poly_1
set_top int_poly
add_files int_poly.c
open_solution "solution1"
set_part {xcu280-fsvh2892-2L-e}
create_clock -period 2






set_directive_pipeline int_poly/loop1 -II 1
set_directive_unroll -factor 1 int_poly/loop1
set_directive_array_partition -type cyclic -factor 1 int_poly x
set_directive_array_partition -type cyclic -factor 1 int_poly c
set_directive_array_partition -type cyclic -factor 1 int_poly y
#Every operator
set_directive_allocation -limit 1 -type operation int_poly/loop1 add
set_directive_allocation -limit 1 -type operation int_poly/loop1 fadd
set_directive_allocation -limit 1 -type operation int_poly/loop1 dadd
set_directive_allocation -limit 1 -type operation int_poly/loop1 mul
set_directive_allocation -limit 1 -type operation int_poly/loop1 fmul
set_directive_allocation -limit 1 -type operation int_poly/loop1 dmul
set_directive_allocation -limit 1 -type operation int_poly/loop1 sdiv
set_directive_allocation -limit 1 -type operation int_poly/loop1 fdiv
set_directive_allocation -limit 1 -type operation int_poly/loop1 ddiv
config_schedule -relax_ii_for_timing=0
csynth_design
#cosim_design -rtl verilog
#export_design
export_design -evaluate verilog -format ip_catalog
exit
