./main.sh int_deriche 6 op0.json 1 700
echo "int_deriche" > iic1.txt
./get_results.sh int_deriche 6 1 700 >> iic1.txt
./main.sh int_deriche 14 op0.json 2 700
echo "int_deriche" > iic2.txt
./get_results.sh int_deriche 14 2 700 >> iic2.txt
./main.sh int_deriche 27 op0.json 3 700
echo "int_deriche" > iic3.txt
./get_results.sh int_deriche 27 3 700 >> iic3.txt
./main.sh int_deriche 32 op0.json 4 700
echo "int_deriche" > iic4.txt
./get_results.sh int_deriche 32 4 700 >> iic4.txt
./main.sh int_deriche 39 op0.json 5 700
echo "int_deriche" > iic5.txt
./get_results.sh int_deriche 39 5 700 >> iic5.txt
