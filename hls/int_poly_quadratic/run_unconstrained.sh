./main.sh int_poly_quadratic 138 op0.json 1 700
echo "int_poly_quadratic" > iic1.txt
./get_results.sh int_poly_quadratic 138 1 700 >> iic1.txt
./main.sh int_poly_quadratic 306 op0.json 2 700
echo "int_poly_quadratic" > iic2.txt
./get_results.sh int_poly_quadratic 306 2 700 >> iic2.txt
./main.sh int_poly_quadratic 459 op0.json 3 700
echo "int_poly_quadratic" > iic3.txt
./get_results.sh int_poly_quadratic 459 3 700 >> iic3.txt
./main.sh int_poly_quadratic 612 op0.json 4 700
echo "int_poly_quadratic" > iic4.txt
./get_results.sh int_poly_quadratic 612 4 700 >> iic4.txt
./main.sh int_poly_quadratic 765 op0.json 5 700
echo "int_poly_quadratic" > iic5.txt
./get_results.sh int_poly_quadratic 765 5 700 >> iic5.txt
