#!/bin/bash

# This script creates a latency histogram from cyclictest output.

DATADIR=cyclictest-data
MAXCORES=maxcores
ONECORE=onecore
DATADIRMAX=$DATADIR/$MAXCORES
DATADIRONE=$DATADIR/$ONECORE

if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root to set real-time scheduling with chrt."
  exit 1
fi

mkdir -p $DATADIR
rm -rf $DATADIR/*
mkdir -p $DATADIRMAX
mkdir -p $DATADIRONE

run_test() {
  local label=$1
  local output_dir=$2
  local cyclictest_args=$3

  echo "Running for $label"

  (cyclictest $cyclictest_args >"$output_dir/output") &
  stress --cpu 2 --vm 1 --hdd 1 --timeout 600

}

segregate_output() {
  local output_dir=$1
  local core_count=$2

  grep -v -e "^#" -e "^$" "$output_dir/output" | tr " " "\t" >"$output_dir/histogram"

  for i in $(seq 1 $core_count); do
    column=$((i + 1))
    histname="$output_dir/histogram$i"
    cut -f1,$column "$output_dir/histogram" >"$histname"
  done
}

# Run with all CPUs
all_cores=$(($(grep 'cpu cores' /proc/cpuinfo | uniq | awk '{print $4}') - 1))
run_test "all CPUs" "$DATADIRMAX" "--duration=10m --mlockall --smp --priority=90 -i100 -h400 -q"
#
# # Run with one CPU
run_test "one CPU" "$DATADIRONE" "--duration=10m --mlockall --priority=90 -i100 -h400 -q -t1 -a 2"

segregate_output "$DATADIRMAX" "$all_cores"
segregate_output "$DATADIRONE" 1
