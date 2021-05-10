./main.sh int_poly3 136 ops.json 680 700 1
echo "int_poly3" > ii1.txt
./get_results.sh int_poly3 136 680 700 >> ii1.txt
./main.sh int_poly3 306 ops2.json 612 700 2
echo "int_poly3" > ii2.txt
./get_results.sh int_poly3 306 612 700 >> ii2.txt
./main.sh int_poly3 351 ops3.json 1755 700 3
echo "int_poly3" > ii3.txt
./get_results.sh int_poly3 351 1755 700 >> ii3.txt
./main.sh int_poly3 468 ops4.json 2340 700 4
echo "int_poly3" > ii4.txt
./get_results.sh int_poly3 468 2340 700 >> ii4.txt
./main.sh int_poly3 585 ops5.json 2925 700 5
echo "int_poly3" > ii5.txt
./get_results.sh int_poly3 585 2925 700 >> ii5.txt
