./main.sh int_gaussian 33 op0.json 1 700
echo "int_gaussian" > iic1.txt
./get_results.sh int_gaussian 33 1 700 >> iic1.txt
./main.sh int_gaussian 66 op0.json 2 700
echo "int_gaussian" > iic2.txt
./get_results.sh int_gaussian 66 2 700 >> iic2.txt
./main.sh int_gaussian 102 op0.json 3 700
echo "int_gaussian" > iic3.txt
./get_results.sh int_gaussian 102 3 700 >> iic3.txt
./main.sh int_gaussian 153 op0.json 4 700
echo "int_gaussian" > iic4.txt
./get_results.sh int_gaussian 153 4 700 >> iic4.txt
./main.sh int_gaussian 207 op0.json 5 700
echo "int_gaussian" > iic5.txt
./get_results.sh int_gaussian 207 5 700 >> iic5.txt
