#!/bin/bash

ITERATIONS=15
DURATION=10
PRIORITY=90
SCHED_POLICY=rr

DATADIR=rt_migrate
GRAPHSDIR=graphs
CSVFILE=timings.csv
GRAPHNAME=rt_migrate_plot.png

mkdir -p "$DATADIR" "$GRAPHSDIR"
rm -rf "$DATADIR"/*

for cmd in rt-migrate-test chrt gnuplot; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "Error: $cmd is not installed."
    exit 1
  fi
done

if [[ $EUID -ne 0 ]]; then
  echo "Run as root for real-time scheduling."
  exit 1
fi

echo "iteration normal_ms rt_ms" >"$DATADIR/$CSVFILE"

for i in $(seq 1 $ITERATIONS); do
  start=$(date +%s%N)
  rt-migrate-test -l "$DURATION" >/dev/null
  end=$(date +%s%N)
  dur_normal=$(((end - start) / 1000000))

  start=$(date +%s%N)
  chrt --$SCHED_POLICY $PRIORITY rt-migrate-test -l "$DURATION" >/dev/null
  end=$(date +%s%N)
  dur_rt=$(((end - start) / 1000000))

  echo "$i $dur_normal $dur_rt" >>"$DATADIR/$CSVFILE"
done

cat >"$DATADIR/plot.gnuplot" <<EOF
set terminal png size 800,400
set output "$GRAPHSDIR/$GRAPHNAME"
set title "rt-migrate-test: RT vs Normal"
set xlabel "Iteration"
set ylabel "Duration (ms)"
set grid
set key outside
plot "$DATADIR/$CSVFILE" using 1:2 with linespoints title "Normal", \
     "$DATADIR/$CSVFILE" using 1:3 with linespoints title "Real-Time"
EOF

gnuplot "$DATADIR/plot.gnuplot"

echo "Graph saved to $GRAPHSDIR/$GRAPHNAME"
