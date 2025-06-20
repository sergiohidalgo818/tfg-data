"""
Script to generate a parquet from a h5 file for a synaptic iteration recorded on rtxi
"""

import pandas as pd
import os
import argparse
import h5py
from pandas.core.arrays.interval import Union


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


def name_traduction(name: str, last_name: Union[str, None]) -> str:
    if "PCI" in name or "wave" in name:
        return "live_neuron"
    else:
        if last_name is None:
            return "model_neuron"
        elif last_name == "model_neuron":
            return "model_neuron_2"

    return "model_neuron"


def read_hdf_as_dict(filename: str) -> dict:
    with h5py.File(filename, "r") as f:
        group = f["Trial1/Synchronous Data"]
        dfs = {}
        last_name = None

        for element in group:
            df = read_field_as_df(group, str(element))
            name = name_traduction(element, last_name)
            dfs[name] = df.copy()
            last_name = name

    return dfs


def main(
    directory: str,
    neuron_1_offset: float,
    neuron_2_offset: float,
    neuron_1_scale: float,
    neuron_2_scale: float,
):
    files = os.listdir(directory)

    hdf_files = [f for f in files if f.endswith(".h5")]

    df: pd.DataFrame = pd.DataFrame(
        {
            "x": [],
            "time": [],
        }
    )
    data_dir = "processed-data"

    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    for file in hdf_files:
        hdf_file_dict: dict = read_hdf_as_dict(os.path.join(directory, file))

        min_len: int = min([len(hdf_file_dict[key]) for key in hdf_file_dict.keys()])

        df: pd.DataFrame = pd.DataFrame(
            {
                "time": hdf_file_dict["live_neuron"]["time"][:min_len],
                "live_neuron": hdf_file_dict["live_neuron"]["value"][:min_len].apply(
                    lambda x: x * neuron_1_scale + neuron_1_offset
                ),
                "model_neuron": hdf_file_dict["model_neuron"]["value"][:min_len].apply(
                    lambda x: x * neuron_2_scale + neuron_2_offset
                ),
            }
        )

        full_data_dir = os.path.join(data_dir, directory)
        if not os.path.exists(full_data_dir):
            os.mkdir(full_data_dir)

        full_data_path = os.path.join(full_data_dir, file.replace(".h5", ".parquet"))
        df.to_parquet(full_data_path, index=False)
        print("Data merged on " + full_data_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", type=str, required=True)
    parser.add_argument("-n1o", "--neuron-1-offset", type=float, default=0.0)
    parser.add_argument("-n2o", "--neuron-2-offset", type=float, default=0.0)
    parser.add_argument("-n1s", "--neuron-1-scale", type=float, default=1.0)
    parser.add_argument("-n2s", "--neuron-2-scale", type=float, default=1.0)

    args = parser.parse_args()

    main(
        args.directory,
        args.neuron_1_offset,
        args.neuron_2_offset,
        args.neuron_1_scale,
        args.neuron_2_scale,
    )
