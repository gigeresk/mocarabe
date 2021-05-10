./main.sh int_caprasse 92 ops.json 828 700 1
echo "int_caprasse" > ii1.txt
./get_results.sh int_caprasse 92 828 700 >> ii1.txt
./main.sh int_caprasse 207 ops2.json 828 700 2
echo "int_caprasse" > ii2.txt
./get_results.sh int_caprasse 207 828 700 >> ii2.txt
./main.sh int_caprasse 306 ops3.json 918 700 3
echo "int_caprasse" > ii3.txt
./get_results.sh int_caprasse 306 918 700 >> ii3.txt
./main.sh int_caprasse 324 ops4.json 2916 700 4
echo "int_caprasse" > ii4.txt
./get_results.sh int_caprasse 324 2916 700 >> ii4.txt
./main.sh int_caprasse 405 ops5.json 3645 700 5
echo "int_caprasse" > ii5.txt
./get_results.sh int_caprasse 405 3645 700 >> ii5.txt
