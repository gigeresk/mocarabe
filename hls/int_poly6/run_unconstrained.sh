./main.sh int_poly6 68 op0.json 1 700
echo "int_poly6" > iic1.txt
./get_results.sh int_poly6 68 1 700 >> iic1.txt
./main.sh int_poly6 153 op0.json 2 700
echo "int_poly6" > iic2.txt
./get_results.sh int_poly6 153 2 700 >> iic2.txt
./main.sh int_poly6 306 op0.json 3 700
echo "int_poly6" > iic3.txt
./get_results.sh int_poly6 306 3 700 >> iic3.txt
./main.sh int_poly6 306 op0.json 4 700
echo "int_poly6" > iic4.txt
./get_results.sh int_poly6 306 4 700 >> iic4.txt
./main.sh int_poly6 306 op0.json 5 700
echo "int_poly6" > iic5.txt
./get_results.sh int_poly6 306 5 700 >> iic5.txt
