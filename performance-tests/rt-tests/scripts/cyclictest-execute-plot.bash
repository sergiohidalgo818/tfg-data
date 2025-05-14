#!/bin/bash
# This script is a modified version of osadl one, original script was retrieved from:
# https://www.osadl.org/Create-a-latency-plot-from-cyclictest-hi.bash-script-for-latency-plot.0.html

# This script creates a latency plot from cyclictest output.

DATADIR=cyclictest
GRAPHSDIR=graphs
GRAPHNAME=ciclictest.png

if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root to set real-time scheduling with chrt."
  exit 1
fi

mkdir -p $GRAPHSDIR
mkdir -p $DATADIR

rm -rf $DATADIR/*
# 1. Run cyclictest
cyclictest -l400000 -m -Sp90 -i200 -h400 -q >$DATADIR/output

# 2. Get maximum latency
max=100

# 3. Grep data lines, remove empty lines and create a common field separator
grep -v -e "^#" -e "^$" $DATADIR/output | tr " " "\t" >$DATADIR/histogram

# 4. Set the number of cores, for example
# cores=$(($(grep 'cpu cores' /proc/cpuinfo | uniq | awk '{print $4}') - 1))
cores=4

# 5. Create two-column data sets with latency classes and frequency values for each core, for example
for i in $(seq 1 $cores); do
  column=$(expr $i + 1)
  histname="$DATADIR/histogram$i"
  cut -f1,$column $DATADIR/histogram >$histname
done

graph="$GRAPHSDIR/$GRAPHNAME"

# 6. Create plot command header
echo -n -e "set title \"Latency plot\"\n\
set terminal png\n\
set xlabel \"Latency (us), max $max us\"\n\
set logscale y\n\
set xrange [0:400]\n\
set yrange [0.8:*]\n\
set ylabel \"Number of latency samples\"\n\
set output \"$graph\"\n\
plot " >$DATADIR/plotcmd

# 7. Append plot command data references
for i in $(seq 1 $cores); do
  if test $i != 1; then
    echo -n ", " >>$DATADIR/plotcmd
  fi
  cpuno=$(expr $i - 1)
  if test $cpuno -lt 10; then
    title=" CPU$cpuno"
  else
    title="CPU$cpuno"
  fi
  echo -n "\"$DATADIR/histogram$i\" using 1:2 title \"$title\" with histeps" >>$DATADIR/plotcmd
done

# 8. Execute plot command
gnuplot -persist <$DATADIR/plotcmd
