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

            function updateOutputMetadata(outputMetadata){
                for (let scl in scl_dict){
                    scl_dict[scl] = scl_dict[scl] / count;
                }
                outputMetadata.userdata = {"scl": scl_dict}
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


def main():

    # set configuration
    CLIENT_ID = ''
    CLIENT_SECRET = ''

    config = SHConfig()
    if CLIENT_ID and CLIENT_SECRET:
        config.sh_client_id = CLIENT_ID
        config.sh_client_secret = CLIENT_SECRET

    if config.sh_client_id == '' or config.sh_client_secret == '':
        print("Warning! To use Sentinel Hub services, please provide the credentials (client ID and client secret).")



    # time TODO -> what time frames
    start_time = datetime.datetime(2020, 1, 1)
    end_time = datetime.datetime(2020, 11, 1)

    # divide into weeks
    n_chunks = 2
    #n_chunks = 44
    tdelta = (end_time - start_time) / n_chunks
    edges = [(start_time + i * tdelta).date().isoformat() for i in range(n_chunks)]
    slots = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]



    # set coordinates, bounding box and a resolution (Naklo) TODO
    # [Longitude (x), Latitude (y) ... ]
    betsiboka_coords_wgs84 = [14.2864, 46.2335, 14.3741, 46.2912]
    resolution = 10
    betsiboka_bbox = BBox(bbox=betsiboka_coords_wgs84, crs=CRS.WGS84)
    betsiboka_size = bbox_to_dimensions(betsiboka_bbox, resolution=resolution)

    print(f'Image shape at {resolution} m resolution: {betsiboka_size} pixels')


    # create a list of requests
    # list_of_requests = [get_true_color_request(slot, betsiboka_bbox, betsiboka_size, config) for slot in slots]
    list_of_requests_pre = [get_classification_request(slot, betsiboka_bbox, betsiboka_size, config) for slot in slots]
    list_of_requests = [request.download_list[0] for request in list_of_requests_pre]

    # download data with multiple threads
    data = SentinelHubDownloadClient(config=config).download(list_of_requests, max_threads=5)

    true_color_imgs = data[0]

    print(f'Returned data is of type = {type(true_color_imgs)} and length {len(true_color_imgs)}.')
    # print(
    #     f'Single element in the list is of type {type(true_color_imgs[-1])} and has shape {true_color_imgs[-1].shape}')

    image = true_color_imgs["default.tif"]
    print(f'Image type: {image.dtype}')

    # plot function
    # factor 1/255 to scale between 0-1
    # factor 3.5 to increase brightness
    plot_image(image, factor=3.5 / 255, clip_range=(0, 1))


api = Flask(__name__)
CORS(api, support_credentials=True)


@api.route('/api', methods=['POST'])
def magic_endpoint():
    payload = request.get_json()

    lat = float(payload['lat'])
    lng = float(payload['lng'])

    print("Received coordinates: (" + str(lat) + ", " + str(lng) + ")")

    # TODO Actually call logic.
    response = jsonify({'bbox': [[lat + 0.05, lng - 0.05], [lat - 0.05, lng + 0.05]]})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


if __name__ == "__main__":
    start = time.time()
    main()
    api.run()
    print("Time taken: " + str(time.time() - start))
