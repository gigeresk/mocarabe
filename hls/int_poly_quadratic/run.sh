./main.sh int_poly_quadratic 138 ops.json 552 700 1
echo "int_poly_quadratic" > ii1.txt
./get_results.sh int_poly_quadratic 138 552 700 >> ii1.txt
./main.sh int_poly_quadratic 306 ops2.json 612 700 2
echo "int_poly_quadratic" > ii2.txt
./get_results.sh int_poly_quadratic 306 612 700 >> ii2.txt
./main.sh int_poly_quadratic 459 ops3.json 1836 700 3
echo "int_poly_quadratic" > ii3.txt
./get_results.sh int_poly_quadratic 459 1836 700 >> ii3.txt
./main.sh int_poly_quadratic 612 ops4.json 2448 700 4
echo "int_poly_quadratic" > ii4.txt
./get_results.sh int_poly_quadratic 612 2448 700 >> ii4.txt
./main.sh int_poly_quadratic 765 ops5.json 3060 700 5
echo "int_poly_quadratic" > ii5.txt
./get_results.sh int_poly_quadratic 765 3060 700 >> ii5.txt
