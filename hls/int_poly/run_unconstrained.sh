./main.sh int_poly 90 op0.json 1 700
echo "int_poly" > iic1.txt
./get_results.sh int_poly 90 1 700 >> iic1.txt
./main.sh int_poly 306 op0.json 2 700
echo "int_poly" > iic2.txt
./get_results.sh int_poly 306 2 700 >> iic2.txt
./main.sh int_poly 306 op0.json 3 700
echo "int_poly" > iic3.txt
./get_results.sh int_poly 306 3 700 >> iic3.txt
./main.sh int_poly 468 op0.json 4 700
echo "int_poly" > iic4.txt
./get_results.sh int_poly 468 4 700 >> iic4.txt
./main.sh int_poly 585 op0.json 5 700
echo "int_poly" > iic5.txt
./get_results.sh int_poly 585 5 700 >> iic5.txt
