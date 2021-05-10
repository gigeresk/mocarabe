./main.sh int_bellido 90 ops.json 720 700 1
echo "int_bellido" > ii1.txt
./get_results.sh int_bellido 90 720 700 >> ii1.txt
./main.sh int_bellido 207 ops2.json 621 700 2
echo "int_bellido" > ii2.txt
./get_results.sh int_bellido 207 621 700 >> ii2.txt
./main.sh int_bellido 306 ops3.json 612 700 3
echo "int_bellido" > ii3.txt
./get_results.sh int_bellido 306 612 700 >> ii3.txt
./main.sh int_bellido 408 ops4.json 3264 700 4
echo "int_bellido" > ii4.txt
./get_results.sh int_bellido 408 3264 700 >> ii4.txt
./main.sh int_bellido 510 ops5.json 4080 700 5
echo "int_bellido" > ii5.txt
./get_results.sh int_bellido 510 4080 700 >> ii5.txt
