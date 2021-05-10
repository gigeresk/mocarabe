./main.sh int_fig3 170 op0.json 1 700
echo "int_fig3" > iic1.txt
./get_results.sh int_fig3 170 1 700 >> iic1.txt
./main.sh int_fig3 306 op0.json 2 700
echo "int_fig3" > iic2.txt
./get_results.sh int_fig3 306 2 700 >> iic2.txt
./main.sh int_fig3 459 op0.json 3 700
echo "int_fig3" > iic3.txt
./get_results.sh int_fig3 459 3 700 >> iic3.txt
./main.sh int_fig3 612 op0.json 4 700
echo "int_fig3" > iic4.txt
./get_results.sh int_fig3 612 4 700 >> iic4.txt
./main.sh int_fig3 765 op0.json 5 700
echo "int_fig3" > iic5.txt
./get_results.sh int_fig3 765 5 700 >> iic5.txt
