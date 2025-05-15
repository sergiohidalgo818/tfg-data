"""
Script to merge the data from the h5 files
"""

import pandas as pd
import os
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


def main():
    files = os.listdir(".")

    priority_folders = [f for f in files if f.startswith("priority")]

    nano_to_micro = 1000

    df: pd.DataFrame = pd.DataFrame(
        {
            "priority": [],
            "duration": [],
            "time_step": [],
            "latency": [],
            "jitter": [],
        }
    )
    for priority_folder in priority_folders:
        files = os.listdir(priority_folder)

        for file in files:
            if file.endswith(".h5"):
                priority_num: int = int(priority_folder.split("-")[1])
                hdf_file_dict: dict = read_hdf_as_dict(
                    os.path.join(priority_folder, file)
                )

                min_len: int = min(
                    len(hdf_file_dict["duration"]),
                    len(hdf_file_dict["time_step"]),
                    len(hdf_file_dict["latency"]),
                    len(hdf_file_dict["jitter"]),
                )

                df_aux: pd.DataFrame = pd.DataFrame(
                    {
                        "priority": [priority_num] * min_len,
                        "time": hdf_file_dict["duration"]["time"][:min_len],
                        "duration": hdf_file_dict["duration"]["value"][:min_len].apply(
                            lambda x: x / nano_to_micro
                        ),
                        "time_step": hdf_file_dict["time_step"]["value"][
                            :min_len
                        ].apply(lambda x: x / nano_to_micro),
                        "latency": hdf_file_dict["latency"]["value"][:min_len].apply(
                            lambda x: x / nano_to_micro
                        ),
                        "jitter": hdf_file_dict["jitter"]["value"][:min_len].apply(
                            lambda x: x / nano_to_micro
                        ),
                        "stress": ["no" not in file] * min_len,
                    }
                )
                df = pd.concat([df, df_aux], ignore_index=True)

    df["priority"] = df["priority"].astype("int32")
    df["time"] = df["time"].astype("int64")

    df.sort_values(by=["priority", "time"], inplace=True)

    data_dir = "merged-data"
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    df.to_parquet(data_dir + "/data.parquet", index=False)
    print("Data merged on " + data_dir + "/data.parquet")


if __name__ == "__main__":
    main()
