import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse


def plot_priorities(df: pd.DataFrame, graphs_dir: str):
    """
    Plots all priorities general graphs with stress, without stress and with both
    """

    for priority in sorted(df["priority"].unique()):
        df_priority = df[df["priority"] == priority]

        for stress_state, label_suffix in [
            (None, ""),  # Combined
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
            plt.xlabel("Sample Index")
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
        (None, ""),
        (True, "-stress"),
        (False, "-no-stress"),
    ]:
        df_filtered = df if stress_state is None else df[df["stress"] == stress_state]

        plt.figure(figsize=(10, 5))

        for priority in sorted(df_filtered["priority"].unique()):
            df_priority = df_filtered[df_filtered["priority"] == priority]
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
        plt.xlabel("Sample Index")
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

    output_path = os.path.join(graphs_dir, f"{measure}_exceeds_{maximum}.png")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Data ploted under {output_path}")


def plot_measures_deviation_number(
    df: pd.DataFrame, maximums: dict[str, int], graphs_dir: str
):
    """
    Plot histograms of how many values exceed the given maximum for each measure,
    grouped by priority and stress.
    """
    os.makedirs(graphs_dir, exist_ok=True)

    measures = ["duration", "time_step", "latency", "jitter"]

    for measure in measures:
        max_value = maximums.get(measure)
        if max_value is None:
            max_value = 100
        plot_measure_deviation_number(df, measure, max_value, graphs_dir)


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
        "--measure", type=str, required=True, help="Name of the measure to plot"
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
        "--measure", type=str, help="Name of the measure to plot", default="latency"
    )
    pmd_parser.add_argument("--maximum", type=int, help="Maximum value")
    pmd_parser.add_argument("--data", type=str, default="merged-data/data.parquet")
    pmd_parser.add_argument("--out", type=str, default="graphs")

    a_parser = subparsers.add_parser("plot-all", help="Plot all")
    a_parser.add_argument("--data", type=str, default="merged-data/data.parquet")
    a_parser.add_argument("--out", type=str, default="graphs")

    args = parser.parse_args()
    df = pd.read_parquet(args.data)
    os.makedirs(args.out, exist_ok=True)

    if args.command == "plot-priorities":
        plot_priorities(df, args.out)
    elif args.command == "plot-measures":
        plot_measures(df, args.out)
    elif args.command == "plot-measure":
        plot_measure(df, args.measure, args.out)
    elif args.command == "plot-measures-deviation":
        maxs = {"duration": 100, "time_step": 100, "latency": 100, "jitter": 2}
        plot_measures_deviation_number(df, maxs, args.out)
    elif args.command == "plot-measure-deviation":
        plot_measure_deviation_number(df, args.measure, args.maximum, args.out)

    elif args.command == "plot-all":
        plot_priorities(df, args.out)
        plot_measures(df, args.out)
        plot_measure_deviation_number(df, "latency", 100, args.out)


if __name__ == "__main__":
    main()
