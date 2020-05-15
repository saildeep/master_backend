import numpy as np

from source.raster_data.abstract_raster_data_provider import AbstractRasterDataProvider


class CosSinRasterDataProvider(AbstractRasterDataProvider):

    def getSampleFN(self):
        return _sample

    def _get_init_params(self):
        return self.scale,

    def init_process(self, _scale):
        global scale
        scale = _scale

    def __init__(self, scale: float = 1):
        self.scale = scale
        super(CosSinRasterDataProvider, self).__init__()


def _sample(positions_with_zoom: np.ndarray) -> np.ndarray:
    global scale
    x = positions_with_zoom[0, :]
    y = positions_with_zoom[1, :]
    out = np.zeros_like(positions_with_zoom, dtype=np.uint8)
    out[0, :] = np.sin(scale * x) * 128 + 127
    out[1, :] = np.cos(scale * y) * 128 + 127

    return out
