import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sentinelhub import SHConfig
import time
from sentinelhub import MimeType, CRS, BBox, SentinelHubRequest, SentinelHubDownloadClient, \
    DataCollection, bbox_to_dimensions, DownloadRequest


def plot_image(image, factor=1.0, clip_range = None, **kwargs):
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

    # set coordinates, bounding box and a resolution
    betsiboka_coords_wgs84 = [46.27, 14.15, 46.51, 14.58]
    resolution = 60
    betsiboka_bbox = BBox(bbox=betsiboka_coords_wgs84, crs=CRS.WGS84)
    betsiboka_size = bbox_to_dimensions(betsiboka_bbox, resolution=resolution)

    print(f'Image shape at {resolution} m resolution: {betsiboka_size} pixels')


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

    request_true_color = SentinelHubRequest(
        evalscript=evalscript_true_color,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L1C,
                time_interval=('2020-06-01', '2020-06-13'),
                #mosaicking_order='leastCC'
            )
        ],
        responses=[
            SentinelHubRequest.output_response('default', MimeType.PNG)
        ],
        bbox=betsiboka_bbox,
        size=betsiboka_size,
        config=config
    )

    true_color_imgs = request_true_color.get_data()

    print(f'Returned data is of type = {type(true_color_imgs)} and length {len(true_color_imgs)}.')
    print(
        f'Single element in the list is of type {type(true_color_imgs[-1])} and has shape {true_color_imgs[-1].shape}')

    image = true_color_imgs[0]
    print(f'Image type: {image.dtype}')

    # plot function
    # factor 1/255 to scale between 0-1
    # factor 3.5 to increase brightness
    plot_image(image, factor=3.5 / 255, clip_range=(0, 1))


if __name__ == "__main__":
    start = time.time()
    main()
    print("Time taken: " + str(time.time() - start))
