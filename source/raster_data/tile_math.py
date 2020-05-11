import math
from source.lat_lng import LatLng
from typing import Tuple


class OSMTile():

    def __init__(self, x: int, y: int, zoom: int):
        self.x = x
        self.y = y
        self.zoom = zoom


def latlngToXY(latlng: LatLng, zoom: int) -> Tuple[float, float]:
    lat_deg = latlng.lat
    lon_deg = latlng.lng
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    x = (lon_deg + 180.0) / 360.0 * n
    y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
    return x, y


def latlngToTile(latlng: LatLng, zoom: int) -> OSMTile:
    x, y = latlngToXY(latlng, zoom)
    x_tile = int(x)
    y_tile = int(y)
    return OSMTile(x_tile, y_tile, zoom)
