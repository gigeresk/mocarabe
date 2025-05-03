#!/bin/zsh

# pushd ../


THREADS = 1

# run router
echo "" > log/parallel_test.log
parallel - -progress - -bar - -gnu - j$THREADS - -header: \
  '
  echo ""  
  echo hls/{b}
  bench=`echo {b} | xargs -I\{\} basename \{\} .c`
  echo $bench

  ::: i 0 1 \
  ::: b ` ls vivad_comparison/ | grep ^int_` \
# popd
