import argparse
from load import ImagePNG
import numpy as np
import matplotlib.pyplot as plt


def parse_args():
    parser = argparse.ArgumentParser(description="PNG Metadata Parser")
    parser.add_argument("png_file", type=str, help="Path to the PNG file")
    parser.add_argument(
        "-i",
        "--info",
        action="store_true",
        help="List metadata information of the PNG file",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Displays image in a pop-up window",
    )
    parser.add_argument(
        "-dm",
        "--del-metadata",
        action="store_true",
        help="Delete metadata from the PNG file",
    )
    parser.add_argument(
        "-s",
        "--save",
        type=str,
        help="Saves image in parameters destination",
    )
    parser.add_argument(
        "-cft",
        "--calc-fourier",
        action="store_true",
        help="Calculate the Fourier Transform of the PNG file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    img = ImagePNG(args.png_file)
    if args.del_metadata:
        img.clear_metadata()
    if args.info:
        img.chunks_info()
    if args.show:
        img.show()
    if args.calc_fourier:
        img.fourier_transform()
    if args.save:
        img.save(args.save)




