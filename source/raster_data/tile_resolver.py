import abc
from typing import Tuple
from urllib.request import urlopen
from urllib.error import HTTPError
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


class UniformColorResolver(AbstractTileImageResolver):

    def __init__(self, rgb: Tuple[int, int, int] = (256, 256, 256), size: int = 256):
        self.im = Image.new('RGB', (size, size), rgb).convert('P')

    def __call__(self, tile: OSMTile) -> Image:
        return self.im


class HTTPTileFileResolver(AbstractTileImageResolver):
    def __init__(self, fallback: AbstractTileImageResolver, url_resolver: TileURLResolver = TileURLResolver()):
        self.url_resolver = url_resolver
        self.fallback = fallback
        self.non_existing_tiles = {}

    def __call__(self, tile) -> Image.Image:
        if tile.__str__() in self.non_existing_tiles:
            raise FileNotFoundError(tile.__str__())

        url = self.url_resolver(tile)
        try:
            im = Image.open(urlopen(url))
            return im
        except HTTPError as err:
            if err.code == 404:
                self.non_existing_tiles[tile.__str__()] = True
                raise FileNotFoundError(tile.__str__())
            else:
                raise err
