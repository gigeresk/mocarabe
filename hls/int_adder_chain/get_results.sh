
name=$1
dirName=$name"_"$2"_"$3"_"$4
echo $dirName
cat results/$dirName/solution1/impl/report/verilog/$name"_export.rpt" | tail -n -12 > results.txt
echo results/$dirName/solution1/syn/report/$name"_csynth.rpt" 
cat results/$dirName/solution1/syn/report/$name"_csynth.rpt"  | grep -A5 "Latency" | head -n -2 >> results.txt

IILat=`cat results.txt | grep "loop1" | cut -d"|" -f 3,6 | sed "s/|/,/"`
LUT=`cat results.txt | grep "LUT" | cut -d":" -f 2`
FF=`cat results.txt | grep "FF" | cut -d":" -f 2`
DSP=`cat results.txt | grep "DSP" | cut -d":" -f 2`
BRAM=`cat results.txt | grep "BRAM" | cut -d":" -f 2`
clk=`cat results.txt | grep "post-impl" | cut -d":" -f 2`

echo "BENCH, UNROLL_FACTOR, LUTs, FF, DSP, BRAM,FREQ, Latency, II,"
echo $name, $2, $LUT, $FF, $DSP, $BRAM,  $clk, $IILAT
cat results/$dirName/solution1/syn/report/$name"_csynth.rpt"  | grep -A5 "Latency" 
