import argparse

import pandas as pd

from coordinates import DATUMS, convert_df, get_epsg
from kmz import df_to_kmz_points


def csv_to_kmz(csv_path: str, epsg: str, out_path: str) -> str:
    df = pd.read_csv(csv_path)
    converted = convert_df(df, epsg)
    return df_to_kmz_points(converted, out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert Gauss-Krüger coordinates from CSV to KMZ."
    )
    parser.add_argument(
        "csv_file",
        help="Input CSV with name, este, norte columns",
    )
    parser.add_argument(
        "datum",
        choices=DATUMS.keys(),
        help="Coordinate datum",
    )
    parser.add_argument(
        "faja",
        type=int,
        choices=range(1, 8),
        help="Gauss-Krüger zone (1-7)",
    )
    parser.add_argument("out", help="Output KMZ file")

    args = parser.parse_args()
    epsg = get_epsg(args.datum, args.faja)
    print("Saved:", csv_to_kmz(args.csv_file, epsg, args.out))