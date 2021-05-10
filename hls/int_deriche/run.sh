./main.sh int_deriche 6 ops.json 480 700 1
echo "int_deriche" > ii1.txt
./get_results.sh int_deriche 6 480 700 >> ii1.txt
./main.sh int_deriche 14 ops2.json 546 700 2
echo "int_deriche" > ii2.txt
./get_results.sh int_deriche 14 546 700 >> ii2.txt
./main.sh int_deriche 27 ops3.json 702 700 3
echo "int_deriche" > ii3.txt
./get_results.sh int_deriche 27 702 700 >> ii3.txt
./main.sh int_deriche 32 ops4.json 608 700 4
echo "int_deriche" > ii4.txt
./get_results.sh int_deriche 32 608 700 >> ii4.txt
./main.sh int_deriche 39 ops5.json 624 700 5
echo "int_deriche" > ii5.txt
./get_results.sh int_deriche 39 624 700 >> ii5.txt
