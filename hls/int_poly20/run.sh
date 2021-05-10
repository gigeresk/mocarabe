./main.sh int_poly20 20 ops.json 740 700 1
echo "int_poly20" > ii1.txt
./get_results.sh int_poly20 20 740 700 >> ii1.txt
./main.sh int_poly20 36 ops2.json 648 700 2
echo "int_poly20" > ii2.txt
./get_results.sh int_poly20 36 648 700 >> ii2.txt
./main.sh int_poly20 52 ops3.json 624 700 3
echo "int_poly20" > ii3.txt
./get_results.sh int_poly20 52 624 700 >> ii3.txt
./main.sh int_poly20 81 ops4.json 648 700 4
echo "int_poly20" > ii4.txt
./get_results.sh int_poly20 81 648 700 >> ii4.txt
./main.sh int_poly20 117 ops5.json 702 700 5
echo "int_poly20" > ii5.txt
./get_results.sh int_poly20 117 702 700 >> ii5.txt
