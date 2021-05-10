./main.sh int_poly10 44 op0.json 1 700
echo "int_poly10" > iic1.txt
./get_results.sh int_poly10 44 1 700 >> iic1.txt
./main.sh int_poly10 81 op0.json 2 700
echo "int_poly10" > iic2.txt
./get_results.sh int_poly10 81 2 700 >> iic2.txt
./main.sh int_poly10 153 op0.json 3 700
echo "int_poly10" > iic3.txt
./get_results.sh int_poly10 153 3 700 >> iic3.txt
./main.sh int_poly10 207 op0.json 4 700
echo "int_poly10" > iic4.txt
./get_results.sh int_poly10 207 4 700 >> iic4.txt
./main.sh int_poly10 306 op0.json 5 700
echo "int_poly10" > iic5.txt
./get_results.sh int_poly10 306 5 700 >> iic5.txt
