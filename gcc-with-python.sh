#!/bin/zsh

#echo $GCC_PLUGIN_PATH
#echo $LD_LIBRARY_PATH

${CC:-gcc-5} -c -fplugin=$GCC_PLUGIN_PATH/python.so -fplugin-arg-python-script=$@


