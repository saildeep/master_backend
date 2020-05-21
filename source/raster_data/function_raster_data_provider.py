import numpy as np

from source.raster_data.abstract_raster_data_provider import AbstractRasterDataProvider


class CosSinRasterDataProvider(AbstractRasterDataProvider):

    def getSampleFN(self):
        return _sample

    def get_init_params(self, opt_manager):
        return self.scale,

    def init_process(self, _scale):
        return _scale

    def __init__(self, scale: float = 1):
        self.scale = scale
        super(CosSinRasterDataProvider, self).__init__()


def _sample(positions_with_zoom: np.ndarray, init_dta) -> np.ndarray:
    x = positions_with_zoom[0, :]
    y = positions_with_zoom[1, :]
    out = np.zeros_like(positions_with_zoom, dtype=np.uint8)
    out[0, :] = np.sin(init_dta * x) * 128 + 127
    out[1, :] = np.cos(init_dta * y) * 128 + 127

    return out
