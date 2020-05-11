import unittest
import os
import tempfile
from source.raster_data.tile_math import OSMTile
from source.raster_data.tile_resolver import HTTPTileFileResolver


class TestHTTPTileFileResolver(unittest.TestCase):
    def test_mainTile(self):
        tile = OSMTile(0, 0, 0)
        resolver = HTTPTileFileResolver()
        path = resolver(tile)
        target_path = os.path.join(tempfile.gettempdir(), 'osmtiles', '0-0-0.png')
        assert target_path == path
        assert os.path.isfile(path)
