./main.sh int_level1_linear 138 ops.json 552 700 1
echo "int_level1_linear" > ii1.txt
./get_results.sh int_level1_linear 138 552 700 >> ii1.txt
./main.sh int_level1_linear 306 ops2.json 612 700 2
echo "int_level1_linear" > ii2.txt
./get_results.sh int_level1_linear 306 612 700 >> ii2.txt
./main.sh int_level1_linear 414 ops3.json 1656 700 3
echo "int_level1_linear" > ii3.txt
./get_results.sh int_level1_linear 414 1656 700 >> ii3.txt
./main.sh int_level1_linear 552 ops4.json 2208 700 4
echo "int_level1_linear" > ii4.txt
./get_results.sh int_level1_linear 552 2208 700 >> ii4.txt
./main.sh int_level1_linear 690 ops5.json 2760 700 5
echo "int_level1_linear" > ii5.txt
./get_results.sh int_level1_linear 690 2760 700 >> ii5.txt
