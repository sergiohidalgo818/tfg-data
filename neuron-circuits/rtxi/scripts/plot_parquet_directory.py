"""
This script plots the end of the synaptic interaction of a parquet file
"""

import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt


def process_and_plot_parquets(directory: str, start: bool = False):
    name_dir = directory.split("/")[1]
    graph_dir = os.path.join("graphs", os.path.basename(os.path.normpath(name_dir)))
    os.makedirs(graph_dir, exist_ok=True)
    max_len = 30000

    for file_name in os.listdir(directory):
        if file_name.endswith(".parquet"):
            file_path = os.path.join(directory, file_name)
            try:
                df = pd.read_parquet(file_path)

                # Check required columns
                if not all(
                    col in df.columns for col in ["time", "live_neuron", "model_neuron"]
                ):
                    print(f"Skipping {file_name}: missing required columns")
                    continue

                if not start:
                    df = df.iloc[len(df) - max_len : len(df)]
                else:
                    df = df.iloc[:max_len]

                plt.figure(figsize=(14, 6))
                plt.plot(df["time"], df["live_neuron"], label="Live Neuron")
                plt.plot(df["time"], df["model_neuron"], label="Model Neuron")
                plt.xlabel("Time Iteration")
                plt.ylabel("Neuron Value (V)")
                plt.title(f"Neuron Activity: {file_name.split('.')[0]}")
                plt.legend()
                plt.margins(0)
                plt.tight_layout()

                if not start:
                    output_file = os.path.join(
                        graph_dir, f"{name_dir}-{os.path.splitext(file_name)[0]}.png"
                    )
                else:
                    output_file = os.path.join(
                        graph_dir,
                        f"{name_dir}-{os.path.splitext(file_name)[0]}-initial.png",
                    )

                plt.savefig(output_file)
                plt.close()
                print(f"Saved plot for {file_name} to {output_file}")
            except Exception as e:
                print(f"Error processing {file_name}: {e}")


def main(directory: str, start: bool):
    process_and_plot_parquets(directory)
    if start:
        process_and_plot_parquets(directory, start)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", type=str, required=True)
    parser.add_argument("-s", "--start", action="store_true")

    args = parser.parse_args()

    main(args.directory, args.start)
