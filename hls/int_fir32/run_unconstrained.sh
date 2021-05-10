./main.sh int_fir32 6 op0.json 1 700
echo "int_fir32" > iic1.txt
./get_results.sh int_fir32 6 1 700 >> iic1.txt
./main.sh int_fir32 18 op0.json 2 700
echo "int_fir32" > iic2.txt
./get_results.sh int_fir32 18 2 700 >> iic2.txt
./main.sh int_fir32 24 op0.json 3 700
echo "int_fir32" > iic3.txt
./get_results.sh int_fir32 24 3 700 >> iic3.txt
./main.sh int_fir32 32 op0.json 4 700
echo "int_fir32" > iic4.txt
./get_results.sh int_fir32 32 4 700 >> iic4.txt
./main.sh int_fir32 39 op0.json 5 700
echo "int_fir32" > iic5.txt
./get_results.sh int_fir32 39 5 700 >> iic5.txt
