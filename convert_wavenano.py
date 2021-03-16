#!/usr/bin/env python3

"""Script to convert all WaveNano output voltammopgram files
   into SACMES compatible files."""

import argparse
from pathlib import Path
from typing import List

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


def convert_files(args: argparse.Namespace) -> None:
    """Read directory from command line and convert files.

    Args:
        args (argparse.Namespace): argparse arguments
    """
    directory: str = args.directory
    my_path: Path = Path(directory)
    files_to_process: List[Path] = list(my_path.rglob("*.csv"))
    for file_path in files_to_process:
        convert_file(file_path)


def convert_file(file_path: Path) -> None:
    """Read info from a wavenano csv export and create sacmes-compatible txt export.

    Args:
        file_path (Path): path to file to be converted
    """
    # Read in the data
    voltage_list: List[str] = []
    current_list: List[str] = []
    with open(file_path, "r", encoding="utf-8") as my_data:
        for line in my_data:
            if line == "":
                continue
            if line.split(",")[0][0] == "P":
                continue
            voltage: str
            current: str
            voltage, current = line.split(",")
            # current = str(float(current) * 1_000_000)git add .
            current = current.rstrip()
            voltage_list.append(voltage)
            current_list.append(current)

    # Find new filename
    shorter_name: str = file_path.name.replace(
        "_Voltammogram_Difference Current vs Average Potential.csv", ".txt"
    )
    output_name: Path = file_path.parent.joinpath(shorter_name)

    # Prepare output file
    output_list: List[str] = []
    for line in HEADER:  # Append boilerplate
        output_list.append(line)

    # values = [x for y in zip(voltage_list, current_list) for x in y]  # FIXME
    for pot, cur in zip(voltage_list, current_list):
        my_line: str = f"{pot}, {cur}, {cur}, {cur}, {cur}, {cur}, {cur}\n"
        output_list.append(my_line)

    file_writer(output_name, output_list)


def file_writer(output_name: Path, output_list: List[str]) -> None:
    """Wrapper to write data to text file.

    Args:
        output_name (Path): path to output file to be created
        output_list (List[str]): list of data lines to write
    """
    with open(output_name, "w", encoding="utf-8") as my_data:
        my_data.writelines(output_list)


def main() -> None:
    """Parse args and convert files."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Directory of Files to process")
    args: argparse.Namespace = parser.parse_args()

    # Perform file conversion
    convert_files(args)


if __name__ == "__main__":
    main()
