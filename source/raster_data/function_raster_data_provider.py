import numpy as np

from source.raster_data.abstract_raster_data_provider import AbstractRasterDataProvider


class CosSinRasterDataProvider(AbstractRasterDataProvider):

    def __init__(self, scale: float = 1):
        self.scale = scale

    def _sample(self, positions_with_zoom: np.ndarray) -> np.ndarray:
        x = positions_with_zoom[0, :]
        y = positions_with_zoom[1, :]
        out = np.zeros_like(positions_with_zoom, dtype=np.uint8)
        out[0, :] = np.sin(self.scale * x) * 128 + 127
        out[1, :] = np.cos(self.scale * y) * 128 + 127

        return out
