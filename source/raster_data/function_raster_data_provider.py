import numpy as np

from source.raster_data.abstract_raster_data_provider import AbstractRasterDataProvider


class CosSinRasterDataProvider(AbstractRasterDataProvider):

    def __init__(self, x_scale: float = 1, y_scale: float = 1):
        self.x_scale = x_scale
        self.y_scale = y_scale

    def _sample(self, positions_with_zoom: np.ndarray) -> np.ndarray:
        x = positions_with_zoom[0, :]
        y = positions_with_zoom[1, :]
        out = np.zeros_like(positions_with_zoom, dtype=np.uint8)
        out[0, :] = np.sin(self.x_scale * x) * 255
        out[1, :] = np.cos(self.y_scale * y) * 255
        return out
