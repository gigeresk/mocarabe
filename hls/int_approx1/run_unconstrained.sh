./main.sh int_approx1 90 op0.json 1 700
echo "int_approx1" > iic1.txt
./get_results.sh int_approx1 90 1 700 >> iic1.txt
./main.sh int_approx1 207 op0.json 2 700
echo "int_approx1" > iic2.txt
./get_results.sh int_approx1 207 2 700 >> iic2.txt
./main.sh int_approx1 306 op0.json 3 700
echo "int_approx1" > iic3.txt
./get_results.sh int_approx1 306 3 700 >> iic3.txt
./main.sh int_approx1 324 op0.json 4 700
echo "int_approx1" > iic4.txt
./get_results.sh int_approx1 324 4 700 >> iic4.txt
./main.sh int_approx1 405 op0.json 5 700
echo "int_approx1" > iic5.txt
./get_results.sh int_approx1 405 5 700 >> iic5.txt
