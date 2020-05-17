import logging
from logging import info
from multiprocessing.dummy import Manager

import numpy as np

from source.lat_lng import LatLng
from source.raster_data.abstract_raster_data_provider import AbstractRasterDataProvider, getInitData
from source.raster_data.tile_cache import FileTileCache, MemoryTileCache
from source.raster_data.tile_math import latlngToTile, latlngToTilePixel, tileExists, latlngZoomToXYZoomNP
from source.raster_data.tile_resolver import AbstractTileImageResolver, HTTPTileFileResolver


class OSMRasterDataProvider(AbstractRasterDataProvider):

    def __init__(self, zoom_offset: int = 0,
                 max_zoom_level: int = 19):
        info("Starting Raster data provider")
        self.zoom_offset = zoom_offset
        self.max_zoom_level = max_zoom_level
        super(OSMRasterDataProvider, self).__init__()

    def init_process(self, file_locks, zoom_offset, max_zoom_level, memdict):
        logging.basicConfig(level=logging.INFO)
        info("Started process")

        process_data = (self.defaultTileResolver(memdict), zoom_offset, max_zoom_level)
        return process_data

    def get_init_params(self, manager: Manager):
        d = {}
        if manager is not None:
            d = manager.dict()

        return None, self.zoom_offset, self.max_zoom_level, d

    def defaultTileResolver(self, dict) -> AbstractTileImageResolver:
        r = HTTPTileFileResolver()
        r = FileTileCache(r)

        r = MemoryTileCache(r, mem_size=1e5, lock=False, storage=dict)  # small cache for th
        r = MemoryTileCache(r, lock=False, storage={})
        return r

    def getSampleFN(self):
        return _sample


def _sample(positions_with_zoom: np.ndarray) -> np.ndarray:
    init_data = getInitData()

    data_source: AbstractTileImageResolver = init_data[0]
    zoom_offset = init_data[1]
    max_zoom = init_data[2]

    lat_array = positions_with_zoom[0, :]
    lng_array = positions_with_zoom[1, :]
    zoom_array = positions_with_zoom[2, :]

    out = np.zeros_like(positions_with_zoom, dtype=np.uint8)

    for i in range(len(lat_array)):
        lat = lat_array[i]
        lng = lng_array[i]
        latlng = LatLng(lat, lng)
        zoom = min(int(zoom_array[i] + zoom_offset), max_zoom)
        tile_image = None
        while tile_image is None and zoom >= 0:
            try:

                tile = latlngToTile(latlng, zoom)
                assert tileExists(tile)
                tile_image = data_source(tile)

            except FileNotFoundError:
                zoom -= 1

        colors = [0, 0, 0]
        if tile_image is not None:

            tile_pixel = latlngToTilePixel(latlng, zoom)

            colors = tile_image.getpixel(tile_pixel)
            if tile_image.mode == 'P':
                colors = tile_image.palette.palette[colors * 3:colors * 3 + 3]
                colors = np.frombuffer(colors, dtype=np.uint8, count=3)
        else:
            logging.warn("Tile out of range " + tile.__str__())
        out[:, i] = colors

    return out
