./main.sh int_iir8 22 op0.json 1 700
echo "int_iir8" > iic1.txt
./get_results.sh int_iir8 22 1 700 >> iic1.txt
./main.sh int_iir8 33 op0.json 2 700
echo "int_iir8" > iic2.txt
./get_results.sh int_iir8 33 2 700 >> iic2.txt
./main.sh int_iir8 52 op0.json 3 700
echo "int_iir8" > iic3.txt
./get_results.sh int_iir8 52 3 700 >> iic3.txt
./main.sh int_iir8 81 op0.json 4 700
echo "int_iir8" > iic4.txt
./get_results.sh int_iir8 81 4 700 >> iic4.txt
./main.sh int_iir8 102 op0.json 5 700
echo "int_iir8" > iic5.txt
./get_results.sh int_iir8 102 5 700 >> iic5.txt
