#!/bin/zsh

parallel --bar --gnu -j32 --header : \
        '
        cd {bench}
        ./run_unconstrained.sh'\
        ::: bench int_adder_chain int_approx1 int_bellido int_caprasse int_dct int_deriche int_fig3 int_fir32 int_gaussian int_iir8 int_level1_linear int_level1_saturation int_poly10 int_poly20 int_poly3 int_poly4 int_poly6 int_poly8 int_poly_quadratic int_rgb int_sobel

