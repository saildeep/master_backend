from io import BytesIO

import math
from flask import Flask, send_file, request
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


def do_projection(lat1, lng1, lat2, lng2, pixel_width=256, pixel_height=256, xmin=-1, xmax=1, ymin=-1,
                  ymax=1,
                  cutoff=math.pi / 6
                  ):

    trange = TargetSectionDescription(xmin, xmax, pixel_width, ymin, ymax, pixel_height)
    c1 = LatLng(lat1, lng1)
    c2 = LatLng(lat2, lng2)
    proj = ComplexLogProjection(c1, c2, cutoff,
                                smoothing_function_type=CosCutoffSmoothingFunction)
    projector = RasterProjector(proj, data_provider)

    d = projector.project(trange)
    pilim = Image.fromarray(d)
    img_io = BytesIO()
    pilim.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


# sample http://127.0.0.1:5000/projection/lat1/10.0/lng1/10.0/lat2/0.0/lng2/0.0.png
@app.route(
    "/projection/lat1/<float(signed=True):lat1>/lng1/<float(signed=True):lng1>/" +
    "lat2/<float(signed=True):lat2>/lng2/<float(signed=True):lng2>.png")
def projection(lat1, lng1, lat2, lng2):
    additional_dict = {}
    if 'width' in request.args:
        additional_dict['pixel_width'] = int(request.args['width'])

    if 'height' in request.args:
        additional_dict['pixel_height'] = int(request.args['height'])

    if 'sizex' in request.args:
        v = float(request.args['sizex'])
        additional_dict['xmin'] = -v
        additional_dict['xmax'] = v

    if 'sizey' in request.args:
        v = float(request.args['sizey'])
        additional_dict['ymin'] = -v
        additional_dict['ymax'] = v



    return do_projection(lat1, lng1, lat2, lng2, **additional_dict)


@app.route('/test')
def test():
    args = request.args
    return "Hello World"
