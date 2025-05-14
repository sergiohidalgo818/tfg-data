set terminal png size 800,400
set output "graphs/rt_migrate_plot_prio_85.png"
set title "rt-migrate-test: RT vs Normal (Priority 85)"
set xlabel "Iteration"
set ylabel "Duration (ms)"
set grid
set key outside
plot "rt_migrate/timings_prio_85.csv" using 1:2 with linespoints title "Normal",      "rt_migrate/timings_prio_85.csv" using 1:3 with linespoints title "Real-Time (prio 85)"
