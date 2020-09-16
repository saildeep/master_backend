import json
import os
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
from server_timing import Timing
import numpy as np

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
app.config.from_mapping(build_cache_config())
cache = Cache(app)
CORS(app)
t = Timing(app,force_debug=True)

from source.hard_coded_providers import get_providers

providers = get_providers()


def do_projection(lat1, lng1, lat2, lng2, data_source: AbstractRasterDataProvider, pixel_width=256, pixel_height=256,
                  xmin=-1, xmax=1, ymin=-1,
                  ymax=1,
                  cutoff=math.pi / 6,
                  smoothing=CosCutoffSmoothingFunction,
                  fileformat='png'
                  ):
    with t.time("setup"):
        trange = TargetSectionDescription(xmin, xmax, pixel_width, ymin, ymax, pixel_height)
        c1 = LatLng(lat1, lng1)
        c2 = LatLng(lat2, lng2)
        proj = ComplexLogProjection(c1, c2, cutoff,
                                    smoothing_function_type=smoothing)
        projector = RasterProjector(proj, data_source)

    with t.time("projection"):
        d = projector.project(trange)
    with t.time("parse_result"):
        pilim = Image.fromarray(d)
    with t.time("convert_to_format"):
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


@app.route(
    "/to_leaflet/lat1/<float(signed=True):lat1>/lng1/<float(signed=True):lng1>/" +
    "lat2/<float(signed=True):lat2>/lng2/<float(signed=True):lng2>/cutoff/<float:cutoff>/smoothing/<smoothing>.json",methods=['POST', 'GET'])
@cross_origin()
def to_leaflet(lat1, lng1, lat2, lng2, cutoff, smoothing):

    if request.method != "POST":
        return ""

    json_i = request.get_json(force=True)
    if json_i is None:
        return "Could not parse JSON",500

    precision = int(request.args.get("precision",5)) # number of digits
    c1latlng = LatLng(lat1, lng1)
    c2latlng = LatLng(lat2, lng2)

    proj = ComplexLogProjection(c1latlng,c2latlng , math.radians(cutoff),
                                smoothing_function_type=parse_smoothing(smoothing))

    center_distance = c1latlng.distanceTo(c2latlng)
    pixel_per_m =  256.0/(156412.0)
    elements =  json_i['data']
    ret_v = []
    for e in elements:
        xy = np.array([[e[0]], [e[0]]])
        xy,clipping = proj(xy,calculate_clipping=True)
        z = proj.getZoomLevel(xy,pixel_per_m)
        latlng = tiling.to_leaflet_LatLng(xy[0,0],xy[1,0])

        clipping = bool(clipping[0])

        ret_element = [ round(latlng.lat,precision), round(latlng.lng,precision),round(z[0],precision),clipping]
        ret_v.append(ret_element)

    z_values = list(map(lambda x:x[2],ret_v))
    min_z = min(*z_values)
    max_z = max(*z_values)
    response = app.response_class(
        response=json.dumps({"data":ret_v,"min_z":min_z,"max_z":max_z},check_circular=False,indent=None),
        status=200,
        mimetype='application/json'
    )

    return response

def get_cities():

    cities_cache_key = "cities_cache_key"
    with t.time("checking_cities_cache"):
        cached_v = cache.get(cities_cache_key)
    if cached_v is not None:
        with t.time("loading_cities_cache"):
            return cached_v

    with t.time("loading_cities_from_file"):
        cities_path = os.path.join(os.path.dirname(__file__),'..',"cities.json")
        with open(cities_path,'rb') as f:
            cities_parsed = json.load(f)

        named_cities = list(filter(lambda x:"name" in x['tags'],cities_parsed['elements']))

        cities_parsed['elements'] = list(map(lambda x:{
            "lat":x['lat'],
            "lon":x['lon'],
            "type":x['type'],
            "tags":{
                "name":x["tags"]["name"],
                "population":x['tags'].get("population",0),
                "place":x['tags']['place']
            }
        },named_cities))
    with t.time("writing_cities_to_cache"):
        cache.set(cities_cache_key,cities_parsed)
    return cities_parsed


@app.route('/cities.json',methods=["GET"])
@cache.cached(timeout=60*60)
def cities():
    cities_static_string = json.dumps(get_cities(), check_circular=False)
    return app.response_class(
        response=cities_static_string,
        status=200,
        mimetype='application/json'
    )





@app.route(
    "/cities_projected/lat1/<float(signed=True):lat1>/lng1/<float(signed=True):lng1>/" +
    "lat2/<float(signed=True):lat2>/lng2/<float(signed=True):lng2>/cutoff/<float:cutoff>/smoothing/<smoothing>.json",methods=['POST', 'GET'])
@cross_origin()
@cache.cached(timeout=60*60*24,key_prefix=make_url_cache_key)
def cities_projected(lat1, lng1, lat2, lng2, cutoff, smoothing):

    with t.time("loading_cities_lat_lng"):
        cities_lat_lng = np.array(list(map(lambda e: [e['lat'], e['lon']], get_cities()['elements']))).transpose()
    with t.time("parsing_params"):
        precision = int(request.args.get("precision",5)) # number of digits
        c1latlng = LatLng(lat1, lng1)
        c2latlng = LatLng(lat2, lng2)

        proj = ComplexLogProjection(c1latlng,c2latlng , math.radians(cutoff),
                                    smoothing_function_type=parse_smoothing(smoothing))

        center_distance = c1latlng.distanceTo(c2latlng)
        pixel_per_m =  256.0/(156412.0)
        num_cities = cities_lat_lng.shape[1]

    with t.time("projection"):
        xy,clipping = proj(cities_lat_lng,calculate_clipping=True)
    with t.time("zoomlevel"):
        z = proj.getZoomLevel(xy, pixel_per_m)
    with t.time("tiling"):
        latlngs = [None] * num_cities
        for i in range(num_cities):

            latlng = tiling.to_leaflet_LatLng(xy[0,i],xy[1,i])
            latlngs[i]=latlng
    with t.time("packaging"):
        ret_v = [None] * num_cities
        p_x_int = 10**precision
        p_x_float = 10.**precision
        my_round = lambda x:int(x*(p_x_int))/(p_x_float)
        for i in range(num_cities):
            clipping_v = bool(clipping[i])
            latlng = latlngs[i]
            ret_element = [ my_round(latlng.lat), my_round(latlng.lng),my_round(z[i]),clipping_v]
            ret_v[i] =ret_element

    with t.time("assembly"):
        z_values = list(map(lambda x:x[2],ret_v))
        min_z = min(*z_values)
        max_z = max(*z_values)
        response = app.response_class(
            response=json.dumps({"data":ret_v,"min_z":min_z,"max_z":max_z},check_circular=False,indent=None),
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