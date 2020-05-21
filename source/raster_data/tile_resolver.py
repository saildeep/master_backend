import abc
from io import BytesIO
from typing import Tuple
import requests
import requests.exceptions as httpex
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
    def __init__(self, url_resolver: TileURLResolver = TileURLResolver()):
        self.url_resolver = url_resolver

        self.non_existing_tiles = {}

    def __call__(self, tile) -> Image.Image:
        if tile.__str__() in self.non_existing_tiles:
            raise FileNotFoundError(tile.__str__())

        url = self.url_resolver(tile)

        data = requests.get(url)
        if data.status_code == 200:
            im = Image.open(BytesIO(data.content)).copy()
            return im
        elif data.status_code == 404:
            self.non_existing_tiles[tile.__str__()] = True
            raise FileNotFoundError(tile.__str__())
        else:
            raise EnvironmentError("Status code " + str(data.status_code))
