import json
from io import BytesIO
from typing import Dict, Type

import math
from flask import Flask, send_file, request, abort, Response, jsonify
from flask_caching import  Cache
import logging

from flask_cors import CORS, cross_origin

from source.complex_log_projection import ComplexLogProjection
from source.lat_lng import LatLng
from source.raster_data.abstract_raster_data_provider import AbstractRasterDataProvider
from source.cache_settings import build_cache_config, make_url_cache_key
from source.raster_data.remote_raster_data_provider import RemoteRasterDataProvider
from source.raster_projector import RasterProjector, TargetSectionDescription
from source.smoothing_functions import CosCutoffSmoothingFunction, AbstractSmoothingFunction, DualCosSmoothingFunction
from source.raster_data.tile_resolver import  TileURLResolver
from PIL import Image
from source.flat_tiling import FlatTiling
import numpy as np

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
app.config.from_mapping(build_cache_config())
cache = Cache(app)
CORS(app)

from source.hard_coded_providers import get_providers

providers = get_providers()


def do_projection(lat1, lng1, lat2, lng2, data_source: AbstractRasterDataProvider, pixel_width=256, pixel_height=256,
                  xmin=-1, xmax=1, ymin=-1,
                  ymax=1,
                  cutoff=math.pi / 6,
                  smoothing=CosCutoffSmoothingFunction,
                  fileformat='png'
                  ):
    trange = TargetSectionDescription(xmin, xmax, pixel_width, ymin, ymax, pixel_height)
    c1 = LatLng(lat1, lng1)
    c2 = LatLng(lat2, lng2)
    proj = ComplexLogProjection(c1, c2, cutoff,
                                smoothing_function_type=smoothing)
    projector = RasterProjector(proj, data_source)

    d = projector.project(trange)
    pilim = Image.fromarray(d)
    img_io = BytesIO()
    pilim.save(img_io,fileformat)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/'+fileformat)


# sample http://127.0.0.1:5000/projection/lat1/10.0/lng1/10.0/lat2/0.0/lng2/0.0.png
@app.route(
    "/projection/lat1/<float(signed=True):lat1>/lng1/<float(signed=True):lng1>/" +
    "lat2/<float(signed=True):lat2>/lng2/<float(signed=True):lng2>.png")

def projection(lat1, lng1, lat2, lng2):
    additional_dict = parse_request_args(request.args)
    additional_dict.update(parse_angle(request.args))
    data_source = parse_source(request.args)
    return do_projection(lat1, lng1, lat2, lng2, data_source, **additional_dict)


tiling = FlatTiling(3 * math.pi)


@app.route(
    "/tile/lat1/<float(signed=True):lat1>/lng1/<float(signed=True):lng1>/" +
    "lat2/<float(signed=True):lat2>/lng2/<float(signed=True):lng2>/cutoff/<float:cutoff>/smoothing/<smoothing>/<int:zoom>/<int(signed=True):x>/<int(signed=True):y>.<string:fileformat>")
@cache.cached(timeout=60*60*24*7,key_prefix=make_url_cache_key)
def tile(lat1, lng1, lat2, lng2, cutoff, smoothing, zoom, x, y,fileformat):
    allowed_formats =  ["png","webp"]
    if fileformat not in allowed_formats:
        return "file format needs to by of type " + str(allowed_formats), 400
    xmin, ymin, xmax, ymax = tiling(x, y, zoom)
    ad = {}
    logging.info("Rendering tile with ({0},{1}) to ({2},{3})".format(xmin, ymin, xmax, ymax))
    source = parse_source(request.args)

    for i in range(5):
        try:
            projected = do_projection(lat1, lng1, lat2, lng2, source, xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax,cutoff= math.radians(cutoff),smoothing=parse_smoothing(smoothing),fileformat=fileformat)
            return projected
        except ConnectionError as e:
            logging.warning(e)

    logging.warning(request.url +" "+ str(request.args) +  "could not be resolved!")
    return "" ,500


@app.route(
    "/resolve/lat1/<float(signed=True):lat1>/lng1/<float(signed=True):lng1>/" +
    "lat2/<float(signed=True):lat2>/lng2/<float(signed=True):lng2>/cutoff/<float:cutoff>/smoothing/<smoothing>"+
    "/clickLat/<float(signed=True):clickLat>/clickLng/<float(signed=True):clickLng>.json")
def resolve(lat1, lng1, lat2, lng2, cutoff, smoothing, clickLat, clickLng):
    proj = ComplexLogProjection(LatLng(lat1, lng1), LatLng(lat2, lng2), math.radians(cutoff),
                                smoothing_function_type=parse_smoothing(smoothing))

    x, y = tiling.from_leaflet_LatLng(LatLng(clickLat, clickLng))

    xy = np.array([[x], [y]])
    latlng_data = proj.invert(xy)


    assert latlng_data.shape == (2, 1)
    ret_data = {"lat": latlng_data[0, 0], "lng": latlng_data[1, 0]}
    response = app.response_class(
        response=json.dumps(ret_data),
        status=200,
        mimetype='application/json'
    )
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.route(
    "/from_leaflet/lat1/<float(signed=True):lat1>/lng1/<float(signed=True):lng1>/" +
    "lat2/<float(signed=True):lat2>/lng2/<float(signed=True):lng2>/cutoff/<float:cutoff>/smoothing/<smoothing>.json",methods=['POST', 'GET'])
@cross_origin(origin='*',headers=['access-control-allow-origin','Content-Type'])
def from_leaflet(lat1, lng1, lat2, lng2, cutoff, smoothing):

    if request.method != "POST":
        return ""

    json_i = request.get_json(force=True)
    if json_i is None:
        return "Could not parse JSON",500



    proj = ComplexLogProjection(LatLng(lat1, lng1), LatLng(lat2, lng2), math.radians(cutoff),
                                smoothing_function_type=parse_smoothing(smoothing))

    elements =  json_i['data']
    ret_v = []
    for e in elements:
        x, y = tiling.from_leaflet_LatLng(LatLng(e['lat'], e['lng']))
        xy = np.array([[x], [y]])
        latlng_data = proj.invert(xy)
        assert latlng_data.shape == (2, 1)
        ret_element = {"lat": latlng_data[0, 0], "lng": latlng_data[1, 0]}
        ret_v.append(ret_element)
    response = app.response_class(
        response=json.dumps({"data":ret_v}),
        status=200,
        mimetype='application/json'
    )

    return response


@app.route("/providers")
def fetch_providers():
    p = get_providers()
    out_dict ={}
    for prov_name,prov_data in p.items():
        if  isinstance(prov_data,RemoteRasterDataProvider):
            prov_data_r : RemoteRasterDataProvider = prov_data
            res:TileURLResolver = prov_data_r.resolver

            out_dict[prov_name] =res.normalized()

    response = jsonify(out_dict)
    return add_cors_headers(response)

def parse_request_args(args: request) -> Dict:
    additional_dict = {}
    if 'width' in args:
        additional_dict['pixel_width'] = int(args['width'])

    if 'height' in args:
        additional_dict['pixel_height'] = int(args['height'])

    if 'sizex' in args:
        v = float(args['sizex'])
        additional_dict['xmin'] = -v
        additional_dict['xmax'] = v

    if 'sizey' in args:
        v = float(args['sizey'])
        additional_dict['ymin'] = -v
        additional_dict['ymax'] = v



def parse_angle(args) -> Dict:
    additional_dict = {}
    # cutoff is provided as degree
    if 'cutoff' in args:
        v = abs(float(args['cutoff']) * math.pi / 180)
        additional_dict['cutoff'] = v

    return additional_dict

def parse_source(args) -> AbstractRasterDataProvider:
    data_source = providers.get("default", None)
    if 'source' in args:
        v = args['source']
        if v not in providers:
            return abort(Response("invalid source"))
        data_source = providers.get(v, None)

    if data_source is None:
        abort(Response("No data source set"))
    return data_source

def parse_smoothing(smoothing) -> Type[AbstractSmoothingFunction]:
    types = {
        "cos":CosCutoffSmoothingFunction,
        "dualcos":DualCosSmoothingFunction
    }

    if smoothing in types:
        return types[smoothing]

    raise Exception("Invalid smoothing type "  + smoothing)



@app.route('/test')
def test():
    args = request.args
    return json.dumps(args)


def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response