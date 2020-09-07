"""
Used for mapping the projection to a tiled space and back
Also has some tricks for leaflet coordinate calculations
"""
from typing import Tuple

from source.lat_lng import LatLng
from source.raster_data.tile_math import latlngToXY, XYToLatLng


class FlatTiling():
    def __init__(self, top_level_range):
        assert top_level_range > 0
        self.top_level_range = top_level_range

        self.start_x = -top_level_range
        self.start_y = -top_level_range

    def __call__(self, x: int, y: int, zoom: int):
        zoom_size = 2 ** zoom

        tile_width = self.top_level_range * 2 / zoom_size

        xmin = x * tile_width + self.start_x
        ymin = y * tile_width + self.start_y
        xmax = xmin + tile_width
        ymax = ymin + tile_width

        return (xmin, ymin, xmax, ymax)

    def from_leaflet_LatLng(self, latlng: LatLng) -> Tuple[float, float]:
        ref = [0, 0]
        latlngToXY(latlng, 0, ref=ref)
        x = ref[0]
        y = ref[1]
        assert 0 <= x <= 1
        assert 0 <= y <= 1
        x = (x * 2 * self.top_level_range) - self.top_level_range
        y = (y * 2 * self.top_level_range) - self.top_level_range
        return x, y

    def to_leaflet_LatLng(self,x,y)->LatLng:

        x = (x + self.top_level_range) / (2* self.top_level_range)
        y = (y+self.top_level_range) / (2*self.top_level_range)
        assert 0 <= x <= 1
        assert 0 <= y <= 1
        return XYToLatLng(x,y)
