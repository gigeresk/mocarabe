./main.sh int_poly8 55 ops.json 770 700 1
echo "int_poly8" > ii1.txt
./get_results.sh int_poly8 55 770 700 >> ii1.txt
./main.sh int_poly8 117 ops2.json 819 700 2
echo "int_poly8" > ii2.txt
./get_results.sh int_poly8 117 819 700 >> ii2.txt
./main.sh int_poly8 207 ops3.json 828 700 3
echo "int_poly8" > ii3.txt
./get_results.sh int_poly8 207 828 700 >> ii3.txt
./main.sh int_poly8 306 ops4.json 918 700 4
echo "int_poly8" > ii4.txt
./get_results.sh int_poly8 306 918 700 >> ii4.txt
./main.sh int_poly8 306 ops5.json 612 700 5
echo "int_poly8" > ii5.txt
./get_results.sh int_poly8 306 612 700 >> ii5.txt
