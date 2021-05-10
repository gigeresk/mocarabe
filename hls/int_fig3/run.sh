./main.sh int_fig3 170 ops.json 510 700 1
echo "int_fig3" > ii1.txt
./get_results.sh int_fig3 170 510 700 >> ii1.txt
./main.sh int_fig3 306 ops2.json 918 700 2
echo "int_fig3" > ii2.txt
./get_results.sh int_fig3 306 918 700 >> ii2.txt
./main.sh int_fig3 459 ops3.json 1377 700 3
echo "int_fig3" > ii3.txt
./get_results.sh int_fig3 459 1377 700 >> ii3.txt
./main.sh int_fig3 612 ops4.json 1836 700 4
echo "int_fig3" > ii4.txt
./get_results.sh int_fig3 612 1836 700 >> ii4.txt
./main.sh int_fig3 765 ops5.json 2295 700 5
echo "int_fig3" > ii5.txt
./get_results.sh int_fig3 765 2295 700 >> ii5.txt
