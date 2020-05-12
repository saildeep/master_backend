import unittest

from source.raster_data.tile_math import OSMTile
from source.raster_data.tile_resolver import HTTPTileFileResolver


class TestHTTPTileFileResolver(unittest.TestCase):
    def test_mainTile(self):
        tile = OSMTile(0, 0, 0)
        resolver = HTTPTileFileResolver()
        image = resolver(tile)
        assert image.height == 256
