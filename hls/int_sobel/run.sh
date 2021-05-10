./main.sh int_sobel 50 ops.json 750 700 1
echo "int_sobel" > ii1.txt
./get_results.sh int_sobel 50 750 700 >> ii1.txt
./main.sh int_sobel 102 ops2.json 714 700 2
echo "int_sobel" > ii2.txt
./get_results.sh int_sobel 102 714 700 >> ii2.txt
./main.sh int_sobel 153 ops3.json 612 700 3
echo "int_sobel" > ii3.txt
./get_results.sh int_sobel 153 612 700 >> ii3.txt
./main.sh int_sobel 207 ops4.json 621 700 4
echo "int_sobel" > ii4.txt
./get_results.sh int_sobel 207 621 700 >> ii4.txt
./main.sh int_sobel 207 ops5.json 621 700 5
echo "int_sobel" > ii5.txt
./get_results.sh int_sobel 207 621 700 >> ii5.txt
