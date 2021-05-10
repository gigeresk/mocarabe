./main.sh int_caprasse 92 op0.json 1 700
echo "int_caprasse" > iic1.txt
./get_results.sh int_caprasse 92 1 700 >> iic1.txt
./main.sh int_caprasse 207 op0.json 2 700
echo "int_caprasse" > iic2.txt
./get_results.sh int_caprasse 207 2 700 >> iic2.txt
./main.sh int_caprasse 306 op0.json 3 700
echo "int_caprasse" > iic3.txt
./get_results.sh int_caprasse 306 3 700 >> iic3.txt
./main.sh int_caprasse 324 op0.json 4 700
echo "int_caprasse" > iic4.txt
./get_results.sh int_caprasse 324 4 700 >> iic4.txt
./main.sh int_caprasse 405 op0.json 5 700
echo "int_caprasse" > iic5.txt
./get_results.sh int_caprasse 405 5 700 >> iic5.txt
