import math
from source.lat_lng import LatLng
from typing import Tuple
import numpy as np


class OSMTile():

    def __init__(self, x: int, y: int, zoom: int):
        self.x = x
        self.y = y
        self.zoom = zoom

    def __hash__(self):
        return hash((self.x, self.y, self.zoom))

    def __str__(self):
        return str(self.x) + '-' + str(self.y) + "-" + str(self.zoom)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.zoom == other.zoom


def latlngToXY(latlng: LatLng, zoom: int) -> Tuple[float, float]:
    lat_deg = latlng.lat
    lon_deg = latlng.lng
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    x = (lon_deg + 180.0) / 360.0 * n
    y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
    return x, y


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


def latlngToTile(latlng: LatLng, zoom: int) -> OSMTile:
    x, y = latlngToXY(latlng, zoom)
    x_tile = int(x)
    y_tile = int(y)
    return OSMTile(x_tile, y_tile, zoom)


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
