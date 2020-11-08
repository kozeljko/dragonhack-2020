import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sentinelhub import SHConfig
import time
from sentinelhub import MimeType, CRS, BBox, SentinelHubRequest, SentinelHubDownloadClient, \
    DataCollection, bbox_to_dimensions, DownloadRequest
import datetime
from flask import Flask, json, request, jsonify
from flask_cors import CORS
from dragonWeather import weatherDragons, get_bounding_box


def plot_image(image, factor=1.0, clip_range=None, **kwargs):
    """
    Utility function for plotting RGB images.
    """
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 15))
    if clip_range is not None:
        ax.imshow(np.clip(image * factor, *clip_range), **kwargs)
    else:
        ax.imshow(image * factor, **kwargs)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.show()


def get_true_color_request(time_interval, betsiboka_bbox, betsiboka_size, config):

    evalscript_true_color = """
        //VERSION=3
        function setup() {
            return {
                input: [{
                    bands: ["B02", "B03", "B04"] // B, G, R
                }],
                output: { bands: 3 }
            };
        }
        function evaluatePixel(sample) {
            return [sample.B04, sample.B03, sample.B02];
        }
    """

    return SentinelHubRequest(
        evalscript=evalscript_true_color,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L1C,
                time_interval=time_interval,
                mosaicking_order='leastCC'
            )
        ],
        responses=[
            SentinelHubRequest.output_response('default', MimeType.PNG)
        ],
        bbox=betsiboka_bbox,
        size=betsiboka_size,
        config=config
    )


def get_classification_request(time_interval, betsiboka_bbox, betsiboka_size, config):

    # color map for classification
    evalscript_classification = """
            //VERSION=3
            var val_names = ["no_data", "defective", "dark area", "cloud shadow", "vegetation", "bare soil",
                "water", "clouds low", "clouds mid", "clouds hi", "cirrus", "snow"];
            var colorMap = {
                0: [0,0,0], // no data
                1: [1,0,0.016], // saturated / defective
                2: [0.525,0.525,0.525], // dark area
                3: [0.467,0.298,0.043], // cloud shadow
                4: [0.063,0.827,0.176], // vegetation
                5: [1,1,0.325], // bare soils
                6: [0,0,1], // water
                7: [0.506, 0.506, 0.506], // Clouds low probability / Unclassified
                8: [0.753, 0.753, 0.753], // Clouds medium probability
                9: [0.949, 0.949, 0.949], // Clouds high probability
                10: [0.733, 0.773, 0.925], // Cirrus
                11: [0.325, 1, 0.980], // Snow / Ice
            }

            function setup() {
                return {
                    input: [{
                        bands: ["B02", "B03", "B04", "SCL"] // B, G, R
                    }],
                    output: { bands: 3 }
                };
            }

            var scl_dict = {};
            var count = 0;
            function evaluatePixel(sample) {
                scl = sample.SCL;
                if (!(val_names[scl] in scl_dict)){
                    scl_dict[val_names[scl]] = 0;
                } else {
                    scl_dict[val_names[scl]] += 1;
                }
                count += 1;
                return colorMap[scl];
            }

            function updateOutputMetadata(scenes, inputMetadata, outputMetadata){
                for (let scl in scl_dict){
                    scl_dict[scl] = scl_dict[scl] / count;
                }
                outputMetadata.userData = {"scl": scl_dict}
            }
        """

    return SentinelHubRequest(
        evalscript=evalscript_classification,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=time_interval,
                mosaicking_order='leastCC'
            )
        ],
        responses=[
            SentinelHubRequest.output_response('default', MimeType.TIFF),
            SentinelHubRequest.output_response('userdata', MimeType.JSON)
        ],
        bbox=betsiboka_bbox,
        size=betsiboka_size,
        config=config
    )


def snowyVegetation(betsiboka_bbox, betsiboka_size, config):

    start_time = datetime.datetime(2018, 1, 1)
    end_time = datetime.datetime(2020, 11, 1)

    # divide into weeks
    # n_chunks = 12 + 1
    n_chunks = 68 + 1
    tdelta = (end_time - start_time) / n_chunks
    edges = [(start_time + i * tdelta).date().isoformat() for i in range(n_chunks)]
    slots = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]

    # create a list of requests
    # list_of_requests = [get_true_color_request(slot, betsiboka_bbox, betsiboka_size, config) for slot in slots]
    list_of_requests_pre = [get_classification_request(slot, betsiboka_bbox, betsiboka_size, config) for slot in slots]
    list_of_requests = [request.download_list[0] for request in list_of_requests_pre]

    # download data with multiple threads
    data = SentinelHubDownloadClient(config=config).download(list_of_requests, max_threads=10)

    res = []
    for i, img in enumerate(data):
        image = img["default.tif"]
        classes = img["userdata.json"]["scl"]
        classes["date"] = datetime.datetime.strptime(edges[i], '%Y-%m-%d').date().replace(day=1)
        res.append(classes)

    df = pd.DataFrame(res)
    # df = df.fillna(0)

    proc = pd.DataFrame()
    proc['date'] = df.groupby(['date'], sort=True)['date'].max()
    proc['vegetation'] = df.groupby(['date'], sort=True)['vegetation'].max().round(decimals=2)
    # proc['snow'] = df.groupby(['date'], sort=True)['snow'].max().round(decimals=2)

    # return only for vegetation
    values = proc.to_numpy()
    res = []
    for i in range(0, len(values)):
        res.append({"time": values[i, 0].isoformat(), "value": values[i, 1]})
    return res


api = Flask(__name__)
CORS(api, support_credentials=True)


@api.route('/api', methods=['POST'])
def magic_endpoint():
    payload = request.get_json()

    lat = float(payload['lat'])
    lng = float(payload['lng'])

    print("Received coordinates: (" + str(lat) + ", " + str(lng) + ")")
    payload = do_magic(lat, lng)

    response = jsonify(payload)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


def do_magic(lat, lng):
    payload = {}

    # set configuration
    CLIENT_ID = ''
    CLIENT_SECRET = ''

    config = SHConfig()
    if CLIENT_ID and CLIENT_SECRET:
        config.sh_client_id = CLIENT_ID
        config.sh_client_secret = CLIENT_SECRET

    if config.sh_client_id == '' or config.sh_client_secret == '':
        print("Warning! To use Sentinel Hub services, please provide the credentials (client ID and client secret).")

    # set coordinates, bounding box and a resolution (Naklo) TODO -> use input coordinates
    # [Longitude (x1), Latitude (y1) ... ]
    # betsiboka_coords_wgs84 = [14.2864, 46.2335, 14.3741, 46.2912]  # Naklo
    # betsiboka_coords_wgs84 = [14.3964, 46.2369, 14.4555, 46.2744]  # Sencur
    bbox = get_bounding_box(lat, lng, 10000)
    payload['bbox'] = [[bbox[0], bbox[3]], [bbox[2], bbox[1]]]

    #if 1 == 1:
    #    return payload

    resolution = 40
    betsiboka_bbox = BBox(bbox=bbox, crs=CRS.WGS84)
    betsiboka_size = bbox_to_dimensions(betsiboka_bbox, resolution=resolution)

    print(f'Image shape at {resolution} m resolution: {betsiboka_size} pixels')

    # get snow and vegetation data
    weatherData = weatherDragons(bbox)
    payload['weather'] = weatherData

    vegData = snowyVegetation(betsiboka_bbox, betsiboka_size, config)
    payload['vegetation'] = vegData

    # print(payload)

    return payload


if __name__ == "__main__":
    start = time.time()
    api.run()
    # do_magic(8.49750009121942, 4.54936981201172)
    print("Time taken: " + str(time.time() - start))
