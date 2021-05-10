./main.sh int_dct 12 ops.json 648 700 1
echo "int_dct" > ii1.txt
./get_results.sh int_dct 12 648 700 >> ii1.txt
./main.sh int_dct 27 ops2.json 729 700 2
echo "int_dct" > ii2.txt
./get_results.sh int_dct 27 729 700 >> ii2.txt
./main.sh int_dct 44 ops3.json 748 700 3
echo "int_dct" > ii3.txt
./get_results.sh int_dct 44 748 700 >> ii3.txt
./main.sh int_dct 66 ops4.json 858 700 4
echo "int_dct" > ii4.txt
./get_results.sh int_dct 66 858 700 >> ii4.txt
./main.sh int_dct 81 ops5.json 810 700 5
echo "int_dct" > ii5.txt
./get_results.sh int_dct 81 810 700 >> ii5.txt
