"""
This script plots the two histograms of cyclic test
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FormatStrFormatter, LogLocator
import seaborn as sns
import os
import glob

FIGSIZE = (12, 7)
BIN_COUNT = 22
EDGE_LINEWIDTH = 0.5
ALPHA = 0.6


def plot_histogram(histogram_dir: str, output_file: str):
    sns.set_theme(style="whitegrid", font_scale=1.2)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    hist_files = sorted(glob.glob(os.path.join(histogram_dir, "histogram[0-9]*")))

    core_samples = {}
    for i, path in enumerate(hist_files):
        df = pd.read_csv(path, sep="\t", header=None, names=["latency_us", "count"])
        samples = np.repeat(df["latency_us"].values, df["count"].astype(int).values)
        core_samples[f"CPU{i}"] = samples

    all_samples = np.concatenate(list(core_samples.values()))
    bins = np.histogram_bin_edges(all_samples, bins=BIN_COUNT)

    fig, ax = plt.subplots(figsize=FIGSIZE)

    colors = sns.color_palette("viridis", len(core_samples))

    for idx, (core, samples) in enumerate(core_samples.items()):
        ax.hist(
            samples,
            bins=bins,
            log=True,
            alpha=ALPHA,
            label=f"{core} (μ={np.mean(samples):.2f}, σ={np.std(samples):.2f})",
            edgecolor="white",
            linewidth=EDGE_LINEWIDTH,
            color=colors[idx],
            histtype="bar",
        )

    ax.set_title("Latency Distribution Per Core", fontsize=16, weight="bold")
    ax.set_xlabel("Latency (µs)", fontsize=13)
    ax.set_ylabel("Count (log scale)", fontsize=13)

    ax.set_yscale("log")
    ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10))
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))

    mean_val = np.mean(all_samples)
    std_val = np.std(all_samples)
    stats_text = f"Mean: {mean_val:.2f} μs\nStd.Dev: {std_val:.2f} μs"
    ax.text(
        0.98,
        0.95,
        stats_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    ax.legend(loc="center right", frameon=True, fancybox=True, framealpha=0.9)
    plt.tight_layout()
    fig.savefig(output_file, dpi=300)
    plt.close(fig)

    print(f"Cyclictest plot saved to: {output_file}")


if __name__ == "__main__":
    plot_histogram("cyclictest-data/maxcores/", "graphs/cyclictest_max_cores.png")
    plot_histogram("cyclictest-data/onecore/", "graphs/cyclictest_one_core.png")
