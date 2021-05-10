

name="poly"
dirName=$name"_"$1

cat results/$dirName/solution1/impl/report/verilog/$name"_export.rpt" | tail -n -12 > results.txt
cat results/$dirName/solution1/syn/report/$name"_csynth.rpt" | sed -n "/Latency\ (/,/======/p" | grep -A100 "Loop:" | head -n -2 >> results.txt

IILat=`cat results.txt | grep "loop1" | cut -d"|" -f 3,6 | sed "s/|/,/"`
LUT=`cat results.txt | grep "LUT" | cut -d":" -f 2`
FF=`cat results.txt | grep "FF" | cut -d":" -f 2`
DSP=`cat results.txt | grep "DSP" | cut -d":" -f 2`
BRAM=`cat results.txt | grep "BRAM" | cut -d":" -f 2`
clk=`cat results.txt | grep "post-impl" | cut -d":" -f 2`

echo "BENCH, UNROLL_FACTOR, LUTs, FF, DSP, BRAM, Latency, II, FREQ"
echo $name, $1, $LUT, $FF, $DSP, $BRAM, $IILat, $clk
