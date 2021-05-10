./main.sh int_poly20 20 op0.json 1 700
echo "int_poly20" > iic1.txt
./get_results.sh int_poly20 20 1 700 >> iic1.txt
./main.sh int_poly20 36 op0.json 2 700
echo "int_poly20" > iic2.txt
./get_results.sh int_poly20 36 2 700 >> iic2.txt
./main.sh int_poly20 52 op0.json 3 700
echo "int_poly20" > iic3.txt
./get_results.sh int_poly20 52 3 700 >> iic3.txt
./main.sh int_poly20 81 op0.json 4 700
echo "int_poly20" > iic4.txt
./get_results.sh int_poly20 81 4 700 >> iic4.txt
./main.sh int_poly20 117 op0.json 5 700
echo "int_poly20" > iic5.txt
./get_results.sh int_poly20 117 5 700 >> iic5.txt
