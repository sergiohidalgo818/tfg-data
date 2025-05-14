import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt


def plot_model_data(directory: str, name_model: str, separator: str):
    if not os.path.exists("graphs/execution_" + name_model + "/"):
        os.makedirs("graphs/execution_" + name_model + "/")

    print("ploting " + name_model)

    files = os.listdir(directory)

    files = [file for file in files if not file.endswith(".h5")]

    for file in files:
        data_frame = pd.read_csv(
            directory + file, sep=separator, decimal=".", names=["time", "x"]
        )
        data_frame = data_frame[["x", "time"]]

        plt.figure(figsize=(12, 6))

        plt.plot(data_frame["time"], data_frame["x"])
        # plt.xlim((data_frame["time"].min(), data_frame["time"].max()))
        # plt.ylim(top=5)
        #
        name = file.split(".")[0] + "_complete"

        plt.xlabel("time (s)")
        plt.ylabel("voltage (mV)")
        plt.title(name)

        plt.savefig("graphs/execution_" + name_model + "/" + name + ".png")
        plt.close()

    for file in files:
        data_frame = pd.read_csv(
            directory + file, sep=separator, decimal=".", names=["time", "x"]
        )
        data_frame = data_frame[["x", "time"]][data_frame["x"].size - 5000 :]

        plt.figure(figsize=(12, 6))

        plt.plot(data_frame["time"], data_frame["x"])
        # plt.xlim((data_frame["time"].min(), data_frame["time"].max()))
        # plt.ylim(top=5)
        #
        name = file.split(".")[0] + "_zoomed"

        plt.xlabel("time (s)")
        plt.ylabel("voltage (mV)")
        plt.title(name)

        plt.savefig("graphs/execution_" + name_model + "/" + name + ".png")
        plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", type=str, required=True)
    parser.add_argument("-s", "--separator", type=str, default=" ")
    args = parser.parse_args()
    plot_model_data(args.directory, args.directory.replace("/", ""), args.separator)
