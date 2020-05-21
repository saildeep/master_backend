import math
from source.lat_lng import LatLng
from typing import Tuple, List, Optional
import numpy as np


class OSMTile():

    def __init__(self, x: int, y: int, zoom: int):
        if __debug__:
            assert isinstance(x, int) and isinstance(y, int) and isinstance(zoom, int)

        self.x = x
        self.y = y
        self.zoom = zoom

    def __hash__(self):
        return 4 ** self.zoom + 2 ** self.zoom * self.x + self.y

    def __str__(self):
        return str(self.x) + '-' + str(self.y) + "-" + str(self.zoom)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.zoom == other.zoom

    def assign(self, x: int, y: int, zoom: int):
        if __debug__:
            assert isinstance(x, int) and isinstance(y, int) and isinstance(zoom, int)
        self.x = x
        self.y = y
        self.zoom = zoom
        return self

    def copy(self):
        return OSMTile(self.x, self.y, self.zoom)


def latlngToXY(latlng: LatLng, zoom: int, ref: Optional[List[float]] = None) -> List[float]:
    lat_deg = latlng.lat
    lon_deg = latlng.lng
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    x = (lon_deg + 180.0) / 360.0 * n
    y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n

    if ref is None:
        return [x, y]
    else:
        ref[0] = x
        ref[1] = y
        return ref


def latlngZoomToXYZoomNP(data: np.ndarray) -> np.ndarray:
    lat_deg = data[0, :]
    lng_deg = data[1, :]
    zoom = data[2, :].astype(int)  # carefull, those get floored in this stage
    lat_rad = lat_deg * (2 * math.pi / 360.0)
    n = np.power(2, zoom)
    x = (lng_deg + 180.0) / 360.0 * n
    y = (1.0 - np.arcsinh(np.tan(lat_rad)) / math.pi) / 2.0 * n
    return np.stack([x, y, zoom], axis=0)


def latlngToTilePixel(latlng: LatLng, zoom: int, tile_size: int = 256) -> Tuple[OSMTile, Tuple[float, float]]:
    x, y = latlngToXY(latlng, zoom)
    x -= int(x)
    y -= int(y)

    x = min(int(x * tile_size), tile_size - 1)
    y = min(int(y * tile_size), tile_size - 1)
    return x, y


latlongtotile_cache = [0, 0]


def latlngToTile(latlng: LatLng, zoom: int, ref: Optional[OSMTile] = None) -> OSMTile:
    if ref is None:
        ref = OSMTile(0, 0, 0)

    _data = latlngToXY(latlng, zoom, ref=latlongtotile_cache)
    x_tile = int(_data[0])
    y_tile = int(_data[1])
    return ref.assign(x_tile, y_tile, zoom)


def tileExists(tile: OSMTile, max_zoom: int = 100) -> bool:
    if tile.zoom < 0:
        return False
    if tile.zoom > max_zoom:
        return False

    if tile.x < 0:
        return False
    if tile.y < 0:
        return False

    r = 2 ** tile.zoom

    if tile.x >= r:
        return False

    if tile.y >= r:
        return False

    return True
