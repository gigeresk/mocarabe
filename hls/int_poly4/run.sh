./main.sh int_poly4 90 ops.json 630 700 1
echo "int_poly4" > ii1.txt
./get_results.sh int_poly4 90 630 700 >> ii1.txt
./main.sh int_poly4 306 ops2.json 918 700 2
echo "int_poly4" > ii2.txt
./get_results.sh int_poly4 306 918 700 >> ii2.txt
./main.sh int_poly4 306 ops3.json 612 700 3
echo "int_poly4" > ii3.txt
./get_results.sh int_poly4 306 612 700 >> ii3.txt
./main.sh int_poly4 468 ops4.json 3276 700 4
echo "int_poly4" > ii4.txt
./get_results.sh int_poly4 468 3276 700 >> ii4.txt
./main.sh int_poly4 585 ops5.json 4095 700 5
echo "int_poly4" > ii5.txt
./get_results.sh int_poly4 585 4095 700 >> ii5.txt
