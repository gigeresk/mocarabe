./main.sh int_iir8 22 ops.json 462 700 1
echo "int_iir8" > ii1.txt
./get_results.sh int_iir8 22 462 700 >> ii1.txt
./main.sh int_iir8 33 ops2.json 462 700 2
echo "int_iir8" > ii2.txt
./get_results.sh int_iir8 33 462 700 >> ii2.txt
./main.sh int_iir8 52 ops3.json 468 700 3
echo "int_iir8" > ii3.txt
./get_results.sh int_iir8 52 468 700 >> ii3.txt
./main.sh int_iir8 81 ops4.json 486 700 4
echo "int_iir8" > ii4.txt
./get_results.sh int_iir8 81 486 700 >> ii4.txt
./main.sh int_iir8 102 ops5.json 510 700 5
echo "int_iir8" > ii5.txt
./get_results.sh int_iir8 102 510 700 >> ii5.txt
