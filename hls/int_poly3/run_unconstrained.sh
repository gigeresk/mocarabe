./main.sh int_poly3 136 op0.json 1 700
echo "int_poly3" > iic1.txt
./get_results.sh int_poly3 136 1 700 >> iic1.txt
./main.sh int_poly3 306 op0.json 2 700
echo "int_poly3" > iic2.txt
./get_results.sh int_poly3 306 2 700 >> iic2.txt
./main.sh int_poly3 351 op0.json 3 700
echo "int_poly3" > iic3.txt
./get_results.sh int_poly3 351 3 700 >> iic3.txt
./main.sh int_poly3 468 op0.json 4 700
echo "int_poly3" > iic4.txt
./get_results.sh int_poly3 468 4 700 >> iic4.txt
./main.sh int_poly3 585 op0.json 5 700
echo "int_poly3" > iic5.txt
./get_results.sh int_poly3 585 5 700 >> iic5.txt
