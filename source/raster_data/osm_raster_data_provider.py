from typing import Optional, List

import numpy as np

from source.lat_lng import LatLng
from source.raster_data.abstract_raster_data_provider import AbstractRasterDataProvider
from source.raster_data.tile_cache import FileTileCache, MemoryTileCache
from source.raster_data.tile_math import latlngToTile, latlngToTilePixel, tileExists
from source.raster_data.tile_resolver import AbstractTileImageResolver, HTTPTileFileResolver

from multiprocessing import Lock


class OSMRasterDataProvider(AbstractRasterDataProvider):

    def __init__(self, tile_resolver: Optional[AbstractTileImageResolver] = None, zoom_offset: int = 4,
                 max_zoom_level: int = 19):



        self.zoom_offset = zoom_offset
        self.max_zoom_level = max_zoom_level
        super(OSMRasterDataProvider, self).__init__()

    def _init_process(self, file_locks,zoom_offset,max_zoom_level):
        print("Started process")
        global process_data
        process_data = (self.defaultTileResolver(file_locks),zoom_offset,max_zoom_level)

    def _get_init_params(self):
        locks = []
        for i in range(4096):
            locks.append(Lock())
        return locks,self.zoom_offset,self.max_zoom_level

    def defaultTileResolver(self, file_locks: List[Lock]) -> AbstractTileImageResolver:

        r = HTTPTileFileResolver()
        r = FileTileCache(r,locks= file_locks )

        r = MemoryTileCache(r, mem_size=1000, lock=False)  # small cache for th
        r = MemoryTileCache(r, lock=False)
        return r

    def _getSampleFN(self):
        return _sample

def _sample( positions_with_zoom: np.ndarray) -> np.ndarray:
    global process_data
    data_source:AbstractTileImageResolver = process_data[0]
    zoom_offset = process_data[1]
    max_zoom = process_data[2]

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

        assert tile_image is not None

        tile_pixel = latlngToTilePixel(latlng, zoom)

        colors = tile_image.getpixel(tile_pixel)
        if tile_image.mode == 'P':
            colors = tile_image.palette.palette[colors * 3:colors * 3 + 3]
            colors = np.frombuffer(colors, dtype=np.uint8, count=3)

        out[:, i] = colors

    return out
