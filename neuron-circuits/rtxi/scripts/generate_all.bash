# Virtual with recorded neuron
uv run scripts/h5_to_parquet.py -d v_hr-r_lp/ -n1o 6 -n2o 0.7 -n2s 1000
uv run scripts/plot_parquet_directory.py -d processed-data/v_hr-r_lp/ -s
