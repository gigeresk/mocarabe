./main.sh int_gaussian 33 ops.json 561 700 1
echo "int_gaussian" > ii1.txt
./get_results.sh int_gaussian 33 561 700 >> ii1.txt
./main.sh int_gaussian 66 ops2.json 528 700 2
echo "int_gaussian" > ii2.txt
./get_results.sh int_gaussian 66 528 700 >> ii2.txt
./main.sh int_gaussian 102 ops3.json 510 700 3
echo "int_gaussian" > ii3.txt
./get_results.sh int_gaussian 102 510 700 >> ii3.txt
./main.sh int_gaussian 153 ops4.json 612 700 4
echo "int_gaussian" > ii4.txt
./get_results.sh int_gaussian 153 612 700 >> ii4.txt
./main.sh int_gaussian 207 ops5.json 414 700 5
echo "int_gaussian" > ii5.txt
./get_results.sh int_gaussian 207 414 700 >> ii5.txt
