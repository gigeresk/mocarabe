#!/bin/bash
echo "Executing main benchmarking script"
if [[ $# -eq 0 ]]; then
echo "ERROR: Missing input arguments: make sure you included benchmark name, unroll factor, operator file path, target frequency"
exit 1
fi

name=$1
unrollFactor=$2
operator_file=$3
NUM_OPERATORS=$4
freq=$5
ii=$6
echo "$name"
echo "this is operator file"
echo $operator_file
cat $operator_file
pwd
#num of each operator
#add
ah=$(cat $operator_file)
echo $AH
ADD=$(cat $operator_file | jq '."+"')
if [[ "$ADD" == "null" ]] ; then
  ADD=0
fi
ADD=$(( ADD*unrollFactor ))
echo "ADD"
echo $ADD
FADD=$(cat $operator_file | jq '."+f"')
if [[ "$FADD" == "null" ]] ; then
  FADD=0
fi
echo $FADD
DADD=$(cat $operator_file | jq '."+d"')
if [[ "$DADD" == "null" ]] ; then
  DADD=0
fi

#mul
MUL=$(cat $operator_file | jq '."*"')
if [[ "$MUL" == "null" ]] ; then
  MUL=0
fi
MUL=$(( MUL*unrollFactor ))
echo "MUL"
echo $MUL
FMUL=$(cat $operator_file | jq '."*f"')
if [[ "$FMUL" == "null" ]] ; then
  FMUL=0
fi
echo $FMUL
DMUL=$(cat $operator_file | jq '."*d"')
if [[ "$DMUL" == "null" ]] ; then
  DMUL=0
fi
echo $DMUL

#div
DIV=$(cat $operator_file | jq '."/"')
if [[ "$DIV" == "null" ]] ; then
  DIV=0
fi
echo $DIV
FDIV=$(cat $operator_file | jq '."/f"')
if [[ "$FDIV" == "null" ]] ; then
  FDIV=0
fi
echo $FDIV
DDIV=$(cat $operator_file | jq '."/d"')
if [[ "$DDIV" == "null" ]] ; then
  DDIV=0
fi
echo $DDIV
echo "that was how many operators there were"
echo $NUM_OPERATORS
#
resultsPath="results"
newName=$name"_"$unrollFactor"_"$NUM_OPERATORS"_"$freq

[ -d $resultsPath ] || mkdir $resultsPath
cp $name".c" $resultsPath
cp $name".tcl" $resultsPath"/"$newName".tcl"
echo "ah"
cd $resultsPath
echo $resultsPath"/"$newName".tcl"
sed -i "s/open_project\(.*\)/open_project $newName/g" $newName".tcl"
#unroll factor
echo "unroll factor:"
echo $unrollFactor
sed -i "s/set_directive_unroll $name\/loop1 -factor \([0-9]*\)/set_directive_unroll $name\/loop1 -factor $unrollFactor/g" $newName".tcl"
#
sed -i "s/set_directive_array_partition -type cyclic -factor \([0-9]*\)/set_directive_array_partition -type cyclic -factor $unrollFactor/g" $newName".tcl"

#ii
sed -i "s/set_directive_pipeline $name\/loop1 -II \([0-9]*\)/set_directive_pipeline $name\/loop1 -II $ii/g" $newName".tcl"
#add
if [[ $ADD != 0 ]]; then 
sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1 add/set_directive_allocation -limit $ADD -type operation $name\/loop1 add/g" $newName".tcl"
else
sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1 add//g" $newName".tcl"
fi

if [[ $FADD != 0 ]]; then 
sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1/loop1 fadd/set_directive_allocation -limit $FADD -type operation $name\/loop1 fadd/g" $newName".tcl"
else
sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1 fadd//g" $newName".tcl"
fi

if [[ $DADD != 0 ]]; then 
sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1 dadd/set_directive_allocation -limit $DADD -type operation $name\/loop1 dadd/g" $newName".tcl"
else
sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1 dadd//g" $newName".tcl"
fi

#mult
if [[ $MUL != 0 ]]; then 
sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1 mul/set_directive_allocation -limit $MUL -type operation $name\/loop1 mul/g" $newName".tcl"
else
sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1 mul//g" $newName".tcl"
fi

if [[ $FMUL != 0 ]]; then 
sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1 fmul/set_directive_allocation -limit $FMUL -type operation $name\/loop1 fmul/g" $newName".tcl"
else
sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1 fmul//g" $newName".tcl"
fi

if [[ $DMUL != 0 ]]; then 

sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1 dmul/set_directive_allocation -limit $DMUL -type operation $name\/loop1 dmul/g" $newName".tcl"
else
sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1 dmul//g" $newName".tcl"
fi

#div
if [[ $DIV != 0 ]]; then 
sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1 sdiv/set_directive_allocation -limit $DIV -type operation $name\/loop1 sdiv/g" $newName".tcl"
else
sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1 sdiv//g" $newName".tcl"
fi

if [[ $FDIV != 0 ]]; then 

sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1 fdiv/set_directive_allocation -limit $FDIV -type operation $name\/loop1 fdiv/g" $newName".tcl"
else
sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1 fdiv//g" $newName".tcl"
fi

if [[ $DDIV != 0 ]]; then 
sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1 ddiv/set_directive_allocation -limit $DDIV -type operation $name\/loop1 ddiv/g" $newName".tcl"
else
sed -i "s/set_directive_allocation -limit \([0-9]*\) -type operation $name\/loop1 ddiv//g" $newName".tcl"
fi

#period
echo $freq
echo "MHz"
sed -i "s/create_clock -period \(.*\)/create_clock -period ${freq}MHz/g" $newName".tcl"

# Rename to specific benchmark if applicable
sed -i "s/generic/$name/g" $newName".tcl" 

echo "into vivado hls $ii"
# vivado_hls -f $newName".tcl" -tclargs $ii
vivado_hls -f $newName".tcl"