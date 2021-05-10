./main.sh int_poly8 55 op0.json 1 700
echo "int_poly8" > iic1.txt
./get_results.sh int_poly8 55 1 700 >> iic1.txt
./main.sh int_poly8 117 op0.json 2 700
echo "int_poly8" > iic2.txt
./get_results.sh int_poly8 117 2 700 >> iic2.txt
./main.sh int_poly8 207 op0.json 3 700
echo "int_poly8" > iic3.txt
./get_results.sh int_poly8 207 3 700 >> iic3.txt
./main.sh int_poly8 306 op0.json 4 700
echo "int_poly8" > iic4.txt
./get_results.sh int_poly8 306 4 700 >> iic4.txt
./main.sh int_poly8 306 op0.json 5 700
echo "int_poly8" > iic5.txt
./get_results.sh int_poly8 306 5 700 >> iic5.txt
