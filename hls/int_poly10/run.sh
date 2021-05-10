./main.sh int_poly10 44 ops.json 792 700 1
echo "int_poly10" > ii1.txt
./get_results.sh int_poly10 44 792 700 >> ii1.txt
./main.sh int_poly10 81 ops2.json 729 700 2
echo "int_poly10" > ii2.txt
./get_results.sh int_poly10 81 729 700 >> ii2.txt
./main.sh int_poly10 153 ops3.json 918 700 3
echo "int_poly10" > ii3.txt
./get_results.sh int_poly10 153 918 700 >> ii3.txt
./main.sh int_poly10 207 ops4.json 828 700 4
echo "int_poly10" > ii4.txt
./get_results.sh int_poly10 207 828 700 >> ii4.txt
./main.sh int_poly10 306 ops5.json 918 700 5
echo "int_poly10" > ii5.txt
./get_results.sh int_poly10 306 918 700 >> ii5.txt
