./main.sh int_dct 12 op0.json 1 700
echo "int_dct" > iic1.txt
./get_results.sh int_dct 12 1 700 >> iic1.txt
./main.sh int_dct 27 op0.json 2 700
echo "int_dct" > iic2.txt
./get_results.sh int_dct 27 2 700 >> iic2.txt
./main.sh int_dct 44 op0.json 3 700
echo "int_dct" > iic3.txt
./get_results.sh int_dct 44 3 700 >> iic3.txt
./main.sh int_dct 66 op0.json 4 700
echo "int_dct" > iic4.txt
./get_results.sh int_dct 66 4 700 >> iic4.txt
./main.sh int_dct 81 op0.json 5 700
echo "int_dct" > iic5.txt
./get_results.sh int_dct 81 5 700 >> iic5.txt
