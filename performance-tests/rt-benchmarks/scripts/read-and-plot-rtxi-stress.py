import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import h5py


def read_field_as_df(group: h5py.File, name: str) -> pd.DataFrame:
    dataset = group[name]
    arr = dataset[:]

    if arr.dtype.names:
        # Dataset estructurado: convertir por campos
        df = pd.DataFrame({name: arr[name] for name in arr.dtype.names})
    else:
        # Dataset simple
        df = pd.DataFrame(arr, columns=["value"])

    return df


def read_hdf_as_dict(filename: str) -> dict:
    with h5py.File(filename, "r") as f:
        group = f["Trial1/Synchronous Data"]
        dfs = {}
        df = read_field_as_df(group, "0 RT Benchmarks OUTPUT 0 Recording Component")
        dfs["duration"] = df

        df = read_field_as_df(group, "0 RT Benchmarks OUTPUT 1 Recording Component")
        dfs["time_step"] = df

        df = read_field_as_df(group, "0 RT Benchmarks OUTPUT 2 Recording Component")
        dfs["latency"] = df

        df = read_field_as_df(group, "0 RT Benchmarks OUTPUT 6 Recording Component")
        dfs["jitter"] = df

    return dfs


def plot_measure_distribution(
    df: pd.DataFrame, measure: str, name: str, graphs_dir: str
):
    """
    For a given measure, plot a combined histogram (bar-style) per priority,
    showing both stress and no-stress data.
    """
    os.makedirs(graphs_dir, exist_ok=True)

    df = df.copy()
    df[measure] = pd.to_numeric(df[measure], errors="coerce")
    df = df.dropna(subset=[measure])
    df = df[df[measure] > 0]
    nano_to_micro = 1000
    df[measure] = df[measure].apply(lambda x: x / nano_to_micro)

    all_values = df[measure]
    bins = np.histogram_bin_edges(all_values, bins=40)

    plt.figure(figsize=(10, 6))

    if not all_values.empty:
        plt.hist(
            all_values,
            bins=bins,
            log=True,
            alpha=0.6,
            label="Stress",
            edgecolor="white",
        )

    plt.title(f"{name.capitalize()} Distribution")
    plt.xlabel(f"{name.capitalize()} (μs)")
    plt.ylabel("Frequency (log scale)")
    plt.legend()
    plt.grid(False)

    mean_val = all_values.mean()
    std_val = all_values.std()
    stats_text = f"Mean: {mean_val:.2f} μs\nStd.Dev: {std_val:.2f} μs"
    plt.text(
        0.98,
        0.95,
        stats_text,
        transform=plt.gca().transAxes,
        fontsize=10,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    filename = f"{name}-distribution-rtxi-test.png"
    output_path = os.path.join(graphs_dir, filename)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    print(f"Data ploted under {output_path}")


if __name__ == "__main__":
    graphs_dir = "graphs"
    directory = "rtxi-stress"
    hdf5_filename = "workload.h5"

    os.makedirs(graphs_dir, exist_ok=True)

    dfs = read_hdf_as_dict(os.path.join(directory, hdf5_filename))

    for key in dfs:
        plot_measure_distribution(dfs[key], "value", key, graphs_dir)
