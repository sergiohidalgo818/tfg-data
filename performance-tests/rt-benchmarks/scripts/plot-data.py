import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import seaborn as sns
import numpy as np


def plot_priorities(df: pd.DataFrame, graphs_dir: str):
    """
    Plots all priorities general graphs with stress, without stress and with both
    """
    min_size = min(
        [
            len(df[df["priority"] == priority])
            for priority in sorted(df["priority"].unique())
        ]
    )
    for priority in sorted(df["priority"].unique()):
        df_priority = df[df["priority"] == priority][:min_size]

        for stress_state, label_suffix in [
            (True, "-stress"),
            (False, "-no-stress"),
        ]:
            if stress_state is not None:
                df_filtered = df_priority[df_priority["stress"] == stress_state]
            else:
                df_filtered = df_priority

            plt.figure(figsize=(12, 6))
            plt.plot(df_filtered["duration"], label="Duration (μs)")
            plt.plot(df_filtered["time_step"], label="Time Step (μs)")
            plt.plot(df_filtered["latency"], label="Latency (μs)")
            plt.plot(df_filtered["jitter"], label="Jitter (μs)")

            title_suffix = (
                " (Stress)"
                if stress_state is True
                else " (No Stress)"
                if stress_state is False
                else ""
            )
            plt.title(f"RT Measures for Priority {int(priority)}{title_suffix}")
            plt.xlabel("Time (μs)")
            plt.ylabel("Time (μs)")
            plt.legend()
            plt.grid(True)

            filename = f"priority-{int(priority)}{label_suffix}.png"
            output_path = os.path.join(graphs_dir, filename)
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()

            print(f"Data ploted under {output_path}")


def plot_measure(df: pd.DataFrame, measure: str, graphs_dir: str):
    """
    Plot one measure across all priorities on the same graph.
    Each line represents a different priority.
    """
    for stress_state, suffix in [
        (True, "-stress"),
        (False, "-no-stress"),
    ]:
        df_filtered = df if stress_state is None else df[df["stress"] == stress_state]

        min_size = min(
            [
                len(df_filtered[df_filtered["priority"] == priority])
                for priority in sorted(df_filtered["priority"].unique())
            ]
        )

        plt.figure(figsize=(10, 5))

        for priority in sorted(df_filtered["priority"].unique()):
            df_priority = df_filtered[df_filtered["priority"] == priority][:min_size]
            plt.plot(
                df_priority[measure].reset_index(drop=True),
                label=f"Priority {priority}",
            )

        title_suffix = (
            " (Stress)"
            if stress_state is True
            else " (No Stress)"
            if stress_state is False
            else ""
        )
        plt.title(f"{measure.capitalize()} by Priority{title_suffix}")
        plt.xlabel("Time (μs)")
        plt.ylabel(f"{measure.capitalize()} (μs)")
        plt.legend()
        plt.grid(True)

        filename = f"{measure}{suffix}.png"
        output_path = os.path.join(graphs_dir, filename)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        print(f"Data ploted under {output_path}")


def plot_measures(df: pd.DataFrame, graphs_dir: str):
    """
    Load the dataset and plot each measure across all priorities.
    """

    measures = ["duration", "time_step", "latency", "jitter"]
    for measure in measures:
        plot_measure(df, measure, graphs_dir)


def plot_measure_deviation_number(
    df: pd.DataFrame, measure: str, maximum: int, graphs_dir: str
):
    """
    Plot one measure histogram of the number of values that exceed the given maximum,
    grouped by priority and stress state.
    """
    os.makedirs(graphs_dir, exist_ok=True)

    df_exceed = df[df[measure] > maximum]

    counts = (
        df_exceed.groupby(["priority", "stress"]).size().reset_index(name="exceeds")
    )

    pivot = counts.pivot(index="priority", columns="stress", values="exceeds").fillna(0)
    pivot = pivot.rename(columns={False: "No Stress", True: "Stress"})

    ax = pivot.plot(kind="bar", figsize=(10, 6))
    ax.set_title(f"Count of {measure} > {maximum} μs")
    ax.set_xlabel("Priority")
    ax.set_ylabel("Number of Exceeding Samples")
    plt.xticks(rotation=0)
    plt.grid(True, axis="y")
    plt.legend(title="Stress")

    output_path = os.path.join(graphs_dir, f"{measure}-exceeds-{maximum}.png")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Data ploted under {output_path}")


def plot_measures_deviation_number(
    df: pd.DataFrame, maximums: dict[str, tuple[int]], graphs_dir: str
):
    """
    Plot histograms of how many values exceed the given maximum for each measure,
    grouped by priority and stress.
    """
    os.makedirs(graphs_dir, exist_ok=True)

    measures = ["duration", "time_step", "latency", "jitter"]

    for measure in measures:
        max_values = maximums.get(measure)

        if max_values is None:
            max_values = (100,)

        for max_value in max_values:
            plot_measure_deviation_number(df, measure, max_value, graphs_dir)


def plot_measure_distribution(df: pd.DataFrame, measure: str, graphs_dir: str):
    """
    For a given measure, plot a combined histogram (bar-style) per priority,
    showing both stress and no-stress data.
    """
    os.makedirs(graphs_dir, exist_ok=True)

    df = df.copy()
    df[measure] = pd.to_numeric(df[measure], errors="coerce")
    df = df.dropna(subset=[measure])
    df = df[df[measure] > 0]

    for priority in sorted(df["priority"].unique()):
        df_priority = df[df["priority"] == priority]
        stress_data = df_priority[df_priority["stress"] == True][measure]
        no_stress_data = df_priority[df_priority["stress"] == False][measure]

        all_values = pd.concat([stress_data, no_stress_data])
        bins = np.histogram_bin_edges(all_values, bins=40)

        plt.figure(figsize=(10, 6))

        if not no_stress_data.empty:
            plt.hist(
                no_stress_data,
                bins=bins,
                log=True,
                alpha=0.6,
                label="No Stress",
                edgecolor="white",
            )
        if not stress_data.empty:
            plt.hist(
                stress_data,
                bins=bins,
                log=True,
                alpha=0.6,
                label="Stress",
                edgecolor="white",
            )

        plt.title(f"{measure.capitalize()} Distribution\nPriority {priority}")
        plt.xlabel(f"{measure.capitalize()} (μs)")
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

        filename = f"{measure}-distribution-priority-{priority}.png"
        output_path = os.path.join(graphs_dir, filename)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        print(f"Data ploted under {output_path}")


def plot_measures_distribution(df: pd.DataFrame, graphs_dir: str):
    """
    Plot histograms (log-scaled y-axis with stats) for all RT measures:
    duration, time_step, latency, jitter.
    """
    os.makedirs(graphs_dir, exist_ok=True)

    measures = ["duration", "time_step", "latency", "jitter"]

    for measure in measures:
        plot_measure_distribution(df, measure, graphs_dir)


def main():
    parser = argparse.ArgumentParser(description="Plot RT benchmark data")
    subparsers = parser.add_subparsers(dest="command", required=True)

    pp_parser = subparsers.add_parser(
        "plot-priorities", help="Plot all measures per priority"
    )
    pp_parser.add_argument("--data", type=str, default="merged-data/data.parquet")
    pp_parser.add_argument("--out", type=str, default="graphs")

    pms_parser = subparsers.add_parser(
        "plot-measures", help="Plot each measure across all priorities"
    )
    pms_parser.add_argument("--data", type=str, default="merged-data/data.parquet")
    pms_parser.add_argument("--out", type=str, default="graphs")

    pm_parser = subparsers.add_parser(
        "plot-measure", help="Plot one specific measure across priorities"
    )
    pm_parser.add_argument(
        "--measure",
        type=str,
        required=True,
        help="Name of the measure to plot",
        choices=["latency", "time_step", "duration", "jitter"],
    )
    pm_parser.add_argument("--data", type=str, default="merged-data/data.parquet")
    pm_parser.add_argument("--out", type=str, default="graphs")

    pmsd_parser = subparsers.add_parser(
        "plot-measures-deviation",
        help="Plot each measure deviation across all priorities",
    )
    pmsd_parser.add_argument("--data", type=str, default="merged-data/data.parquet")
    pmsd_parser.add_argument("--out", type=str, default="graphs")

    pmd_parser = subparsers.add_parser(
        "plot-measure-deviation",
        help="Plot one specific measure deviation across priorities",
    )
    pmd_parser.add_argument(
        "--measure",
        type=str,
        required=True,
        help="Name of the measure to plot",
        choices=["latency", "time_step", "duration", "jitter"],
    )
    pmd_parser.add_argument("--maximum", type=int, help="Maximum value")
    pmd_parser.add_argument("--data", type=str, default="merged-data/data.parquet")
    pmd_parser.add_argument("--out", type=str, default="graphs")

    pmsdis_parser = subparsers.add_parser(
        "plot-measures-distribution",
        help="Plot each measure deviation across all priorities",
    )
    pmsdis_parser.add_argument("--data", type=str, default="merged-data/data.parquet")
    pmsdis_parser.add_argument("--out", type=str, default="graphs")

    pmdis_parser = subparsers.add_parser(
        "plot-measure-distribution",
        help="Plot one specific measure distribution across priorities",
    )
    pmdis_parser.add_argument(
        "--measure",
        type=str,
        required=True,
        help="Name of the measure to plot",
        choices=["latency", "time_step", "duration", "jitter"],
    )
    pmdis_parser.add_argument("--maximum", type=int, help="Maximum value")
    pmdis_parser.add_argument("--data", type=str, default="merged-data/data.parquet")
    pmdis_parser.add_argument("--out", type=str, default="graphs")

    a_parser = subparsers.add_parser("plot-all", help="Plot all")
    a_parser.add_argument("--data", type=str, default="merged-data/data.parquet")
    a_parser.add_argument("--out", type=str, default="graphs")

    args = parser.parse_args()
    df: pd.DataFrame = pd.read_parquet(args.data)
    os.makedirs(args.out, exist_ok=True)

    if args.command == "plot-priorities":
        plot_priorities(df, args.out)
    elif args.command == "plot-measures":
        plot_measures(df, args.out)
    elif args.command == "plot-measure":
        plot_measure(df, args.measure, args.out)
    elif args.command == "plot-measures-deviation":
        maxs = {
            "duration": (
                100,
                120,
            ),
            "time_step": (100,),
            "latency": (10,),
            "jitter": (2,),
        }
        plot_measures_deviation_number(df, maxs, args.out)
    elif args.command == "plot-measure-deviation":
        plot_measure_deviation_number(df, args.measure, args.maximum, args.out)
    elif args.command == "plot-measures-distribution":
        plot_measures_distribution(df, args.out)
    elif args.command == "plot-measure-distribution":
        plot_measure_distribution(df, args.measure, args.out)
    elif args.command == "plot-all":
        plot_priorities(df, args.out)
        plot_measures(df, args.out)
        maxs = {
            "duration": (
                100,
                120,
            ),
            "time_step": (100,),
            "latency": (10,),
            "jitter": (2,),
        }
        plot_measures_deviation_number(df, maxs, args.out)
        plot_measures_distribution(df, args.out)


if __name__ == "__main__":
    main()
