import numpy as np
import pandas as pd
from math import sin, cos, sqrt, atan2


def get_bounding_box(x, y, offset):
    # Earth’s radius, sphere
    R = 6378137

    dLat = offset / R
    dLon = offset / (R * cos(np.pi * y / 180))

    # OffsetPosition, decimal degrees
    y_offset = dLat * 180 / np.pi
    x_offset = dLon * 180 / np.pi

    return [(x - x_offset, y + y_offset),
            (x + x_offset, y + y_offset),
            (x + x_offset, y - y_offset),
            (x - x_offset, y - y_offset)]


def main():
    # get coordinates -> change this to ipyleafy later
    x = float(input("Enter the longitude (x): "))
    y = float(input("Enter the latitude (y): "))
    print(get_bounding_box(x, y, 100))


if __name__ == "__main__":
    main()