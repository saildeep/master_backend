from io import BytesIO

import math
from flask import Flask, send_file
import logging
from source.complex_log_projection import ComplexLogProjection
from source.lat_lng import LatLng
from source.raster_data.osm_raster_data_provider import OSMRasterDataProvider
from source.raster_projector import RasterProjector, TargetSectionDescription
from source.smoothing_functions import CosCutoffSmoothingFunction
from PIL import Image

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
data_provider = OSMRasterDataProvider()


# sample http://127.0.0.1:5000/projection/lat1/10.0/lng1/10.0/lat2/0.0/lng2/0.0.png
@app.route(
    "/projection/lat1/<float(signed=True):lat1>/lng1/<float(signed=True):lng1>/" +
    "lat2/<float(signed=True):lat2>/lng2/<float(signed=True):lng2>.png")
def projection(lat1, lng1, lat2, lng2):
    c1 = LatLng(lat1, lng1)
    c2 = LatLng(lat2, lng2)
    projection = ComplexLogProjection(c1, c2, math.pi / 6,
                                      smoothing_function_type=CosCutoffSmoothingFunction)
    projector = RasterProjector(projection, data_provider)
    trange = TargetSectionDescription(-math.pi * 3, math.pi * 3, 1920, -math.pi, math.pi, 1080)
    d = projector.project(trange)
    pilim = Image.fromarray(d)
    img_io = BytesIO()
    pilim.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


@app.route('/test')
def test():
    return "Hello World"
