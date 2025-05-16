# RT Benchmarks

RT Benchmarks data, scripts and graphs from different executions on `preempt-rt`. 

## Prerrequisites

For installing `uv`, please go to [the official uv page](https://docs.astral.sh/uv/getting-started/installation/).

## Execution

This data have been retrieved by modifying the priority on the realtime threads of *RTXI* for `preempt-rt` Linux kernel. Then, with *RTXI* **Data Recorder**, the results of **RT Benchmarks** have been written in a HDF5 file, this process has been done twice per priority, one without any workload besides *RTXI* itself, and another with the following `stress` command:

```bash
stress -c 4 --vm 20 --vm-bytes 128M --timeout 300
```


## Data treatment

In order to simplifying the analysis of this data, it has been merged into a single parquet file, generated from the HDF5 files. This is done with the script `merge-data.py` under `scripts/` folder. Also, there are some data inside a writing that could be a few registers longer, so it is checked the minimum length of the registers, setting it as the new maximum number of registers that will bee kept for each priority. Also, all the data is in $ns$ so it has been transformed into $\mu s$. The data has been tagged if it was retrieved during a execution with stress.


## Data plot

For plotting all the images, use the following commands:

```bash
uv run scripts/plot-data.py --plot-all
uv run scripts/read-and-plot-rtxi-stress.py
```

