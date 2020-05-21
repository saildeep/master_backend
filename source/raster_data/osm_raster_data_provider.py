import logging
from logging import info
from multiprocessing.dummy import Manager

import numpy as np

from source.lat_lng import LatLng
from source.raster_data.abstract_raster_data_provider import AbstractRasterDataProvider

from source.raster_data.tile_math import latlngToTile, latlngToTilePixel, tileExists, OSMTile
from source.raster_data.tile_resolver import AbstractTileImageResolver


class OSMRasterDataProvider(AbstractRasterDataProvider):
    resolver: AbstractTileImageResolver

    def __init__(self, resolver, zoom_offset: int = 0,
                 max_zoom_level: int = 19, ):
        info("Starting Raster data provider")
        self.zoom_offset = zoom_offset
        self.max_zoom_level = max_zoom_level
        self.resolver = resolver

        super(OSMRasterDataProvider, self).__init__()

    def init_process(self, file_locks, zoom_offset, max_zoom_level, memdict):
        logging.basicConfig(level=logging.INFO)
        info("Started process")

        process_data = (self.resolver, zoom_offset, max_zoom_level)
        return process_data

    def get_init_params(self, manager: Manager):
        d = {}
        if manager is not None:
            d = manager.dict()

        return None, self.zoom_offset, self.max_zoom_level, d

    def getSampleFN(self):
        return _sample


def _sample(positions_with_zoom: np.ndarray, init_data) -> np.ndarray:
    data_source: AbstractTileImageResolver = init_data[0]
    zoom_offset = init_data[1]
    max_zoom = init_data[2]

    lat_array = positions_with_zoom[0, :]
    lng_array = positions_with_zoom[1, :]
    zoom_array = np.minimum(positions_with_zoom[2, :] + zoom_offset, max_zoom).astype(int)

    # xyz = latlngZoomToXYZoomNP(positions_with_zoom)
    # xyz_tile = xyz.astype(int)

    out = np.zeros_like(positions_with_zoom, dtype=np.uint8)
    tile = OSMTile(0, 0, 0)
    latlng = LatLng(20, 29)
    tile_pixel = [0, 0]
    for i in range(len(lat_array)):
        lat = lat_array[i]
        lng = lng_array[i]
        latlng = latlng.assign(lat, lng)
        zoom = int(zoom_array[i])
        tile_image = None
        while tile_image is None and zoom >= 0:
            try:

                tile = latlngToTile(latlng, zoom, ref=tile)
                assert tileExists(tile)
                tile_image = data_source(tile)

            except FileNotFoundError:
                zoom -= 1

        colors = [0, 0, 0]
        if tile_image is not None:

            tile_pixel = latlngToTilePixel(latlng, zoom, ref=tile_pixel)

            fucking_slow_tuple = (tile_pixel[0], tile_pixel[1])
            colors = tile_image.getpixel(fucking_slow_tuple)
            if tile_image.mode == 'P':
                colors = tile_image.palette.palette[colors * 3:colors * 3 + 3]
                colors = np.frombuffer(colors, dtype=np.uint8, count=3)
        else:
            logging.warn("Zoom level " + str(zoom))
            # logging.warn("Tile out of range " + tile.__str__())
        out[:, i] = colors

    return out
