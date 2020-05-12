import abc
from urllib.request import urlopen
from PIL import Image
from source.raster_data.tile_math import OSMTile


class TileURLResolver():
    def __init__(self, url_format: str = "https://a.tile.openstreetmap.de/{2}/{0}/{1}.png"):
        self.url_format = url_format

    def __call__(self, tile: OSMTile) -> str:
        return self.url_format.format(tile.x, tile.y, tile.zoom)


class AbstractTileImageResolver(abc.ABC):

    @abc.abstractmethod
    def __call__(self, tile: OSMTile) -> Image:
        pass


class HTTPTileFileResolver(AbstractTileImageResolver):
    def __init__(self, url_resolver: TileURLResolver = TileURLResolver()):
        self.url_resolver = url_resolver

    def __call__(self, tile) -> Image.Image:
        url = self.url_resolver(tile)
        return Image.open(urlopen(url))
