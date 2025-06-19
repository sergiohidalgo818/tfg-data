# Pico Neuron models

Here are contained the executions for the models in the Raspberry Pico with the Pico Neuron program.

## Scripts

`plot_model.py`: Plots the indicated model, use `--directory` flag for choosing the directory and `--filename` to indicate the name of csv. Here is an example for the Hindmarsh-Rose model:
 
```bash
uv run scripts/plot_model.py -d hr/ -f hindmarsh-rose.csv 
```

## Models

### Hindmarsh-Rose model 

- Directory of data: `hr`
- Directory of graph: `graph/execution_hindmarsh-rose/`

### Hindmarsh-Rose Chaotic model 

- Directory of data: `hr-chaotic`
- Directory of graph: `graph/execution_hindmarsh-rose-chaotic/`


