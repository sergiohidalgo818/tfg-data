set terminal png size 800,400
set output "graphs/rt_migrate_plot_all.png"
set title "rt-migrate-test: RT"
set xlabel "Iteration"
set ylabel "Duration (ms)"
set grid
set key outside
plot "rt_migrate/timings_prio_80.csv" using 1:2 with linespoints title "Real-Time (prio 80)" , "rt_migrate/timings_prio_85.csv" using 1:2 with linespoints title "Real-Time (prio 85)" , "rt_migrate/timings_prio_90.csv" using 1:2 with linespoints title "Real-Time (prio 90)" , "rt_migrate/timings_prio_95.csv" using 1:2 with linespoints title "Real-Time (prio 95)" , "rt_migrate/timings_prio_99.csv" using 1:2 with linespoints title "Real-Time (prio 99)"
