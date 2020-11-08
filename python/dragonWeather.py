import numpy as np
import pandas as pd
from math import sin, cos, sqrt, atan2
from wwo_hist import retrieve_hist_data
import datetime
import time


def get_bounding_box(x, y, offset):
    # Earth’s radius, sphere
    R = 6378137

    dLat = offset / R
    dLon = offset / (R * cos(np.pi * y / 180))

    # OffsetPosition, decimal degrees
    y_offset = dLat * 180 / np.pi
    x_offset = dLon * 180 / np.pi

    return [x + x_offset, y + y_offset,
            x - x_offset, y - y_offset]


def weatherDragons(coordinates):
    # call the weather api and get some weather info
    frequency = 24
    start_date = '08-NOV-2019'
    start_date = '08-SEP-2020'
    end_date = '08-NOV-2020'
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

    # print(hist_weather_data[0])
    data = hist_weather_data[0]
    data['simple_date'] = pd.to_datetime(data['date_time']).dt.to_period('M')
    print(data)

    # TODO group by simple_date and make sum / max for some columns
    print(data.columns)

    result = {}
    for key in ['maxtempC', 'mintempC', 'totalSnow_cm', 'precipMM']:
        iter_date = datetime.date(2019, 11, 8)
        iter_date = datetime.date(2020, 9, 8)
        values = []

        for tuple in data.get(key).iteritems():
            (sth, value) = tuple
            values.append({'time': iter_date.isoformat(), 'value': value})
            iter_date = iter_date + datetime.timedelta(days=1)

        result[key] = values
    return result
