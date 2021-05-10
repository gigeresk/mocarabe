./main.sh int_fir32 6 ops.json 390 700 1
echo "int_fir32" > ii1.txt
./get_results.sh int_fir32 6 390 700 >> ii1.txt
./main.sh int_fir32 18 ops2.json 594 700 2
echo "int_fir32" > ii2.txt
./get_results.sh int_fir32 18 594 700 >> ii2.txt
./main.sh int_fir32 24 ops3.json 504 700 3
echo "int_fir32" > ii3.txt
./get_results.sh int_fir32 24 504 700 >> ii3.txt
./main.sh int_fir32 32 ops4.json 512 700 4
echo "int_fir32" > ii4.txt
./get_results.sh int_fir32 32 512 700 >> ii4.txt
./main.sh int_fir32 39 ops5.json 468 700 5
echo "int_fir32" > ii5.txt
./get_results.sh int_fir32 39 468 700 >> ii5.txt
