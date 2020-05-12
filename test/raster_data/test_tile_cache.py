import unittest

from source.raster_data.tile_cache import MaxZoomLevelCacheRule, FileTileCache
from source.raster_data.tile_math import OSMTile
from source.raster_data.tile_resolver import HTTPTileFileResolver


class TestFileTileCache(unittest.TestCase):
    def test_zoomLevel(self):
        rules = [
            MaxZoomLevelCacheRule(8)
        ]
        fcache = FileTileCache(HTTPTileFileResolver(None), rules)
        t1 = fcache(OSMTile(0, 0, 0))
        assert t1.height == 256
        t2 = fcache(OSMTile(5, 10, 6))
        assert t2.height == 256
        pass
