./main.sh int_sobel 50 op0.json 1 700
echo "int_sobel" > iic1.txt
./get_results.sh int_sobel 50 1 700 >> iic1.txt
./main.sh int_sobel 102 op0.json 2 700
echo "int_sobel" > iic2.txt
./get_results.sh int_sobel 102 2 700 >> iic2.txt
./main.sh int_sobel 153 op0.json 3 700
echo "int_sobel" > iic3.txt
./get_results.sh int_sobel 153 3 700 >> iic3.txt
./main.sh int_sobel 207 op0.json 4 700
echo "int_sobel" > iic4.txt
./get_results.sh int_sobel 207 4 700 >> iic4.txt
./main.sh int_sobel 207 op0.json 5 700
echo "int_sobel" > iic5.txt
./get_results.sh int_sobel 207 5 700 >> iic5.txt
