# Cyclictest

Cyclictest data, scripts and graphs from two different executions on `preempt-rt`. 

## Prerrequisites

For installing `uv`, please go to [the official uv page](https://docs.astral.sh/uv/getting-started/installation/).

## Execution

This data has been retrieved by creating a script that executes `cyclictest` with `chrt`, changing its priority to $90$. This is done two times with a stress test. One is with all available cores, and the other with just one. Both executions take $10$ minutes to complete.

## Data treatment

In order to simplifying the analysis of this data, it has been divided into the number of CPUs that have been used on the execution.

## Data plot

For plotting the two histograms, use the following command:

```bash
uv run scripts/cyclictest-plot.py
```
