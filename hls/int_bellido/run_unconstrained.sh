./main.sh int_bellido 90 op0.json 1 700
echo "int_bellido" > iic1.txt
./get_results.sh int_bellido 90 1 700 >> iic1.txt
./main.sh int_bellido 207 op0.json 2 700
echo "int_bellido" > iic2.txt
./get_results.sh int_bellido 207 2 700 >> iic2.txt
./main.sh int_bellido 306 op0.json 3 700
echo "int_bellido" > iic3.txt
./get_results.sh int_bellido 306 3 700 >> iic3.txt
./main.sh int_bellido 408 op0.json 4 700
echo "int_bellido" > iic4.txt
./get_results.sh int_bellido 408 4 700 >> iic4.txt
./main.sh int_bellido 510 op0.json 5 700
echo "int_bellido" > iic5.txt
./get_results.sh int_bellido 510 5 700 >> iic5.txt
