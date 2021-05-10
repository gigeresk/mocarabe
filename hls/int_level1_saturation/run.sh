./main.sh int_level1_saturation 90 ops.json 630 700 1
echo "int_level1_saturation" > ii1.txt
./get_results.sh int_level1_saturation 90 630 700 >> ii1.txt
./main.sh int_level1_saturation 207 ops2.json 621 700 2
echo "int_level1_saturation" > ii2.txt
./get_results.sh int_level1_saturation 207 621 700 >> ii2.txt
./main.sh int_level1_saturation 306 ops3.json 612 700 3
echo "int_level1_saturation" > ii3.txt
./get_results.sh int_level1_saturation 306 612 700 >> ii3.txt
./main.sh int_level1_saturation 324 ops4.json 2592 700 4
echo "int_level1_saturation" > ii4.txt
./get_results.sh int_level1_saturation 324 2592 700 >> ii4.txt
./main.sh int_level1_saturation 405 ops5.json 3240 700 5
echo "int_level1_saturation" > ii5.txt
./get_results.sh int_level1_saturation 405 3240 700 >> ii5.txt
