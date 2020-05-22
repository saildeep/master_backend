import json
from io import BytesIO
from typing import Tuple, Dict

import math
from flask import Flask, send_file, request, abort, Response
import logging
from source.complex_log_projection import ComplexLogProjection
from source.lat_lng import LatLng
from source.raster_data.abstract_raster_data_provider import AbstractRasterDataProvider
from source.raster_data.osm_raster_data_provider import OSMRasterDataProvider
from source.raster_projector import RasterProjector, TargetSectionDescription
from source.smoothing_functions import CosCutoffSmoothingFunction
from source.raster_data.tile_resolver import HTTPTileFileResolver, TileURLResolver
from source.raster_data.tile_cache import FileTileCache, TileFilenameResolver, MemoryTileCache
from PIL import Image

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


def get_providers() -> Dict[str, AbstractRasterDataProvider]:
    _providers: Dict[str, AbstractRasterDataProvider] = {}

    r = HTTPTileFileResolver(TileURLResolver(
        url_format="https://a.tile.openstreetmap.de/{2}/{0}/{1}.png"))
    r = FileTileCache(r, TileFilenameResolver("osm"))
    r = MemoryTileCache(r, mem_size=100000)
    _providers['default'] = OSMRasterDataProvider(r, max_zoom_level=19)
    _providers['osm'] = _providers['default']

    r = HTTPTileFileResolver(TileURLResolver(
        url_format="https://atlas34.inf.uni-konstanz.de/mbtiles/data/openmaptiles_satellite_lowres/{2}/{0}/{1}.jpg"))
    r = FileTileCache(r, TileFilenameResolver("satellite_lowres"))
    r = MemoryTileCache(r, mem_size=100000)
    _providers['satellite'] = OSMRasterDataProvider(r, max_zoom_level=12)
    return _providers


providers = get_providers()


def do_projection(lat1, lng1, lat2, lng2, data_source: AbstractRasterDataProvider, pixel_width=256, pixel_height=256,
                  xmin=-1, xmax=1, ymin=-1,
                  ymax=1,
                  cutoff=math.pi / 6
                  ):
    trange = TargetSectionDescription(xmin, xmax, pixel_width, ymin, ymax, pixel_height)
    c1 = LatLng(lat1, lng1)
    c2 = LatLng(lat2, lng2)
    proj = ComplexLogProjection(c1, c2, cutoff,
                                smoothing_function_type=CosCutoffSmoothingFunction)
    projector = RasterProjector(proj, data_source)

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
    additional_dict = parse_request_args(request.args)
    data_source = parse_source(request.args)
    return do_projection(lat1, lng1, lat2, lng2, data_source, **additional_dict)


@app.route(
    "/tile/lat1/<float(signed=True):lat1>/lng1/<float(signed=True):lng1>/" +
    "lat2/<float(signed=True):lat2>/lng2/<float(signed=True):lng2>/<int:zoom>/<int:x>/<int:y>.png")
def tile(lat1, lng1, lat2, lng2, zoom, x, y):
    top_level_range = 1  # goes from -top_level_range to top_level_range
    zoom_size = 2 ** zoom
    tile_width = top_level_range * 2 / zoom_size

    start_x = -top_level_range
    start_y = -top_level_range

    xmin = x * tile_width + start_x
    ymin = y * tile_width + start_y
    xmax = xmin + tile_width
    ymax = ymin + tile_width
    logging.info("Rendering tile with ({0},{1}) to ({2},{3})".format(xmin, ymin, xmax, ymax))
    source = parse_source(request.args)

    return do_projection(lat1, lng1, lat2, lng2, source, xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)


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


@app.route('/test')
def test():
    args = request.args
    return json.dumps(args)
