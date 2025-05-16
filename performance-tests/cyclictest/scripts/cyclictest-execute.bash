#!/bin/bash

# This script creates a latency histogram from cyclictest output.

DATADIR=cyclictest-data
MAXCORES=maxcores
ONECORE=onecore
ISOLATED=isocore

DATADIRMAX=$DATADIR/$MAXCORES
DATADIRONE=$DATADIR/$ONECORE
DATADIRISOCORE=$DATADIR/$ISOLATED

if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root to set real-time scheduling."
  exit 1
fi

mkdir -p $DATADIR
rm -rf $DATADIR/*
mkdir -p $DATADIRMAX
mkdir -p $DATADIRONE
mkdir -p $DATADIRISOCORE

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

run_test_isolated() {
  local label=$1
  local output_dir=$2
  local cyclictest_args=$3
  local isolated_cpu=$4

  echo "Running for $label"

  (taskset -c $isolated_cpu cyclictest $cyclictest_args >"$output_dir/output") &
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

segregate_output_singlecore() {
  local output_dir=$1
  local core_num=$2

  grep -v -e "^#" -e "^$" "$output_dir/output" | tr " " "\t" >"$output_dir/histogram"

  column=2
  histname="$output_dir/histogram$core_num"
  cut -f1,$column "$output_dir/histogram" >"$histname"
}

# Run with all CPUs
all_cores=$(grep 'cpu cores' /proc/cpuinfo | uniq | awk '{print $4}')
run_test "all CPUs" "$DATADIRMAX" "--duration=10m --mlockall --smp --priority=90 -i100 -h100 -q"

# Run with one CPU
one_cpu=2
run_test "one CPU" "$DATADIRONE" "--duration=10m --mlockall --priority=90 -i100 -h100 -q -a $one_cpu"

# Run with one isolated CPU
isolated_cpu=5
run_test_isolated "isolated CPU" "$DATADIRISOCORE" "--duration=10m --mlockall --priority=90 -i100 -h100 -q -a $isolated_cpu" $isolated_cpu

segregate_output "$DATADIRMAX" "$all_cores"
segregate_output_singlecore "$DATADIRONE" $one_cpu
segregate_output_singlecore "$DATADIRISOCORE" $isolated_cpu
