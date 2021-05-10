./main.sh int_level1_linear 138 op0.json 1 700
echo "int_level1_linear" > iic1.txt
./get_results.sh int_level1_linear 138 1 700 >> iic1.txt
./main.sh int_level1_linear 306 op0.json 2 700
echo "int_level1_linear" > iic2.txt
./get_results.sh int_level1_linear 306 2 700 >> iic2.txt
./main.sh int_level1_linear 414 op0.json 3 700
echo "int_level1_linear" > iic3.txt
./get_results.sh int_level1_linear 414 3 700 >> iic3.txt
./main.sh int_level1_linear 552 op0.json 4 700
echo "int_level1_linear" > iic4.txt
./get_results.sh int_level1_linear 552 4 700 >> iic4.txt
./main.sh int_level1_linear 690 op0.json 5 700
echo "int_level1_linear" > iic5.txt
./get_results.sh int_level1_linear 690 5 700 >> iic5.txt
