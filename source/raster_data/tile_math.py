from logging import error

import math
from source.lat_lng import LatLng
from typing import List, Optional
import numpy as np


class OSMTile:
    x: int
    y: int
    zoom: int
    _hash: int

    def __init__(self, x: int, y: int, zoom: int):
        self.assign(x, y, zoom)

    def __hash__(self):
        # should be distributed somehow
        return self._hash

    def _calc_hash(self):
        self._hash = 4 * self.zoom + 2 * self.zoom * self.x + self.y

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
        self._calc_hash()
        return self

    def copy(self):
        return OSMTile(self.x, self.y, self.zoom)


def latlngToXY(latlng: LatLng, zoom: int, ref: List[float]) -> List[float]:
    lat_deg = latlng.lat
    lon_deg = latlng.lng
    lat_rad = lat_deg * math.pi / 180
    n = 2.0 ** zoom
    x = (lon_deg + 180.0) / 360.0 * n
    y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n

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


def latlngToTilePixel(latlng: LatLng, zoom: int, tile_size: int = 256, ref: Optional[List[float]] = None) \
        -> List[
            float]:
    if ref is None:
        ref = [0, 0]

    ref = latlngToXY(latlng, zoom, ref=ref)
    ref[0] -= int(ref[0])
    ref[1] -= int(ref[1])

    ref[0] = min(int(ref[0] * tile_size), tile_size - 1)
    ref[1] = min(int(ref[1] * tile_size), tile_size - 1)
    return ref


def latlngToTile(latlng: LatLng, zoom: int, ref: Optional[OSMTile] = None) -> OSMTile:
    if ref is None:
        ref = OSMTile(0, 0, 0)

    _data = latlngToXY(latlng, zoom, ref=[0, 0])  # slow but reliable
    x_tile = int(_data[0])
    y_tile = int(_data[1])
    ref.assign(x_tile, y_tile, zoom)
    if __debug__:
        if not tileExists(ref, 1000000):
            error("Created invalid tile from " + str(latlng) + " with x = " + str(_data[0]) + ", " + str(
                _data[1]) + "z = " + str(zoom))
    return ref


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
