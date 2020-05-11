import tempfile
import os
import wget

from source.raster_data.tile_math import OSMTile


class TileURLResolver():
    def __init__(self, url_format: str = "https://a.tile.openstreetmap.de/{2}/{0}/{1}.png"):
        self.url_format = url_format

    def __call__(self, tile: OSMTile) -> str:
        return self.url_format.format(tile.x, tile.y, tile.zoom)


class TileFilenameResolver():
    def __init__(self):
        self.basedir = os.path.join(tempfile.gettempdir(), "osmtiles")
        if os.path.isfile(self.basedir):
            raise EnvironmentError("File with name of basedir exists")

        if not os.path.isdir(self.basedir):
            os.mkdir(self.basedir)

    def __call__(self, tile: OSMTile) -> str:
        return os.path.join(self.basedir, "{2}-{0}-{1}.png".format(tile.x, tile.y, tile.zoom))


class HTTPTileFileResolver():
    def __init__(self, url_resolver: TileURLResolver = TileURLResolver(),
                 filename_resolver: TileFilenameResolver = TileFilenameResolver()):
        self.url_resolver = url_resolver
        self.filename_resolver = filename_resolver

    def __call__(self, tile):
        url = self.url_resolver(tile)
        file_path = self.filename_resolver(tile)
        if os.path.isfile(file_path):
            return file_path

        downloaded_to = wget.download(url, out=file_path)
        return downloaded_to
