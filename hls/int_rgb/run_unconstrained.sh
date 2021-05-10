./main.sh int_rgb 46 op0.json 1 700
echo "int_rgb" > iic1.txt
./get_results.sh int_rgb 46 1 700 >> iic1.txt
./main.sh int_rgb 81 op0.json 2 700
echo "int_rgb" > iic2.txt
./get_results.sh int_rgb 81 2 700 >> iic2.txt
./main.sh int_rgb 117 op0.json 3 700
echo "int_rgb" > iic3.txt
./get_results.sh int_rgb 117 3 700 >> iic3.txt
./main.sh int_rgb 207 op0.json 4 700
echo "int_rgb" > iic4.txt
./get_results.sh int_rgb 207 4 700 >> iic4.txt
./main.sh int_rgb 207 op0.json 5 700
echo "int_rgb" > iic5.txt
./get_results.sh int_rgb 207 5 700 >> iic5.txt
