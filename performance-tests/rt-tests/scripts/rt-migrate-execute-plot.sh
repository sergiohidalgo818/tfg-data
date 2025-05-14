#!/bin/bash

ITERATIONS=10
DURATION=10
SCHED_POLICY=fifo
PRIORITIES=(80 85 90 95 99)

DATADIR=rt_migrate
GRAPHSDIR=graphs

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

for PRIORITY in "${PRIORITIES[@]}"; do
  CSVFILE="timings_prio_$PRIORITY.csv"
  echo "iteration normal_ms rt_ms" >"$DATADIR/$CSVFILE"

  echo "Running tests for priority $PRIORITY..."
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

  GRAPHNAME="rt_migrate_plot_prio_$PRIORITY.png"

  cat >"$DATADIR/plot_$PRIORITY.gnuplot" <<EOF
set terminal png size 800,400
set output "$GRAPHSDIR/$GRAPHNAME"
set title "rt-migrate-test: RT vs Normal (Priority $PRIORITY)"
set xlabel "Iteration"
set ylabel "Duration (ms)"
set grid
set key outside
plot "$DATADIR/$CSVFILE" using 1:2 with linespoints title "Normal", \
     "$DATADIR/$CSVFILE" using 1:3 with linespoints title "Real-Time (prio $PRIORITY)"
EOF

  gnuplot "$DATADIR/plot_$PRIORITY.gnuplot"
  echo "Graph for priority $PRIORITY saved to $GRAPHSDIR/$GRAPHNAME"
done
