./main.sh int_poly6 68 ops.json 748 700 1
echo "int_poly6" > ii1.txt
./get_results.sh int_poly6 68 748 700 >> ii1.txt
./main.sh int_poly6 153 ops2.json 765 700 2
echo "int_poly6" > ii2.txt
./get_results.sh int_poly6 153 765 700 >> ii2.txt
./main.sh int_poly6 306 ops3.json 918 700 3
echo "int_poly6" > ii3.txt
./get_results.sh int_poly6 306 918 700 >> ii3.txt
./main.sh int_poly6 306 ops4.json 612 700 4
echo "int_poly6" > ii4.txt
./get_results.sh int_poly6 306 612 700 >> ii4.txt
./main.sh int_poly6 306 ops5.json 612 700 5
echo "int_poly6" > ii5.txt
./get_results.sh int_poly6 306 612 700 >> ii5.txt
