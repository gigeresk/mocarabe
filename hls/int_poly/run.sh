./main.sh int_poly 90 ops.json 630 700 1
echo "int_poly" > ii1.txt
./get_results.sh int_poly 90 630 700 >> ii1.txt
./main.sh int_poly 306 ops2.json 918 700 2
echo "int_poly" > ii2.txt
./get_results.sh int_poly 306 918 700 >> ii2.txt
./main.sh int_poly 306 ops3.json 612 700 3
echo "int_poly" > ii3.txt
./get_results.sh int_poly 306 612 700 >> ii3.txt
./main.sh int_poly 468 ops4.json 3276 700 4
echo "int_poly" > ii4.txt
./get_results.sh int_poly 468 3276 700 >> ii4.txt
./main.sh int_poly 585 ops5.json 4095 700 5
echo "int_poly" > ii5.txt
./get_results.sh int_poly 585 4095 700 >> ii5.txt
