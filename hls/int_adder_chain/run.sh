./main.sh int_adder_chain 170 ops.json 510 700 1
echo "int_adder_chain" > ii1.txt
./get_results.sh int_adder_chain 170 510 700 >> ii1.txt
./main.sh int_adder_chain 306 ops2.json 306 700 2
echo "int_adder_chain" > ii2.txt
./get_results.sh int_adder_chain 306 306 700 >> ii2.txt
./main.sh int_adder_chain 306 ops3.json 306 700 3
echo "int_adder_chain" > ii3.txt
./get_results.sh int_adder_chain 306 306 700 >> ii3.txt
./main.sh int_adder_chain 612 ops4.json 1836 700 4
echo "int_adder_chain" > ii4.txt
./get_results.sh int_adder_chain 612 1836 700 >> ii4.txt
./main.sh int_adder_chain 765 ops5.json 2295 700 5
echo "int_adder_chain" > ii5.txt
./get_results.sh int_adder_chain 765 2295 700 >> ii5.txt
