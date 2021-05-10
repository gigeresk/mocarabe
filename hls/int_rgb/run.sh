./main.sh int_rgb 46 ops.json 552 700 1
echo "int_rgb" > ii1.txt
./get_results.sh int_rgb 46 552 700 >> ii1.txt
./main.sh int_rgb 81 ops2.json 567 700 2
echo "int_rgb" > ii2.txt
./get_results.sh int_rgb 81 567 700 >> ii2.txt
./main.sh int_rgb 117 ops3.json 585 700 3
echo "int_rgb" > ii3.txt
./get_results.sh int_rgb 117 585 700 >> ii3.txt
./main.sh int_rgb 207 ops4.json 621 700 4
echo "int_rgb" > ii4.txt
./get_results.sh int_rgb 207 621 700 >> ii4.txt
./main.sh int_rgb 207 ops5.json 414 700 5
echo "int_rgb" > ii5.txt
./get_results.sh int_rgb 207 414 700 >> ii5.txt
