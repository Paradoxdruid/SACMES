#!/usr/bin/env python3

import argparse
from pathlib import Path

# Convert WaveNano Data to SACMES compatible format

HEADER = """Difference:
Ep = -0.376V
ip = 3.842e-7A
Ap = 2.640e-8VA

Forward:

Reverse:
Ep = -0.388V
ip = -1.838e-7A
Ah = -6.283e-9VA

Channel 2:

Difference:
Ep = -0.388V
ip = 1.459e-6A
Ah = 6.023e-8VA

Forward:
Ep = -0.382V
ip = 8.717e-7A
Ah = 3.416e-8VA

Reverse:
Ep = -0.394V
ip = -6.472e-7A
Ah = -2.447e-8VA

Potential/V, i1d/A, i1f/A, i1r/A, i2d/A, i2f/A, i2r/A\n\n"""


def convert_files(args):
    directory = args.directory
    my_path = Path(directory)
    files_to_process = list(my_path.rglob("*.csv"))
    for file_path in files_to_process:
        convert_file(file_path)


def convert_file(file_path):
    # Read in the data
    voltage_list = []
    current_list = []
    with open(file_path, "r", encoding="utf-8") as my_data:
        for line in my_data:
            if line == "":
                continue
            if line.split(",")[0][0] == "P":
                continue
            voltage, current = line.split(",")
            # current = str(float(current) * 1_000_000)
            voltage_list.append(voltage)
            current_list.append(current)

    # Find new filename
    shorter_name = file_path.name.replace(
        "_Voltammogram_Difference Current vs Average Potential.csv", ".txt"
    )

    # Prepare output file
    output_list = []
    for line in HEADER:  # Append boilerplate
        output_list.append(line)

    values = [x for y in zip(voltage_list, current_list) for x in y]
    for each in values:
        output_list.append(each)

    file_writer(shorter_name, output_list)


def file_writer(output_name, output_list):
    with open(output_name, "w", encoding="utf-8") as my_data:
        my_data.writelines(output_list)


def main():
    """Parse args and convert files."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Directory of Files to process")
    args: argparse.Namespace = parser.parse_args()

    # Perform file conversion
    convert_files(args)


# def ReadWaveNanoData(myfile):

#     try:
#         data_dict = {}
#         voltage_list = []
#         current_list = []

# with open(myfile, "r", encoding="utf-8") as mydata:
#     for line in mydata:
#         if line == "":
#             continue
#         if line.split(",")[0][0] == "P":
#             continue
#         voltage, current = line.split(",")
#         current = str(float(current) * 1_000_000)
#         voltage_list.append(voltage)
#         current_list.append(current)
#         data_dict.setdefault(voltage, []).append(current)

#         return voltage_list, current_list, data_dict

#     except Exception:
#         print("\nError in ReadData()\n")


if __name__ == "__main__":
    main()
