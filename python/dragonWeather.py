import numpy as np
import pandas as pd
from math import sin, cos, sqrt, atan2
from wwo_hist import retrieve_hist_data


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


def weatherDragons(coordinates):
    # call the weather api and get some weather info
    frequency = 24
    start_date = '01-OCT-2020' #'01-JAN-2018'
    end_date = '01-NOV-2020'
    api_key = '49ba24e2b3b8412a9e501452200811'
    location_list = [str(coordinates[1]) + "," + str(coordinates[0])]

    hist_weather_data = retrieve_hist_data(api_key,
                                           location_list,
                                           start_date,
                                           end_date,
                                           frequency,
                                           location_label=False,
                                           export_csv=False,
                                           store_df=True)

    print(hist_weather_data)