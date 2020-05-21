import abc

import numpy as np
from source.raster_data import tile_math
from multiprocessing import Pool, cpu_count, Manager


def getInitData():
    global init_data
    return init_data



class AbstractRasterDataProvider(abc.ABC):

    def __init__(self):
        manager = Manager()

        self._init_data = self.init_process(*self.get_init_params(None))


    @abc.abstractmethod
    def init_process(self, *args):
        pass

    def _init_process(self, fn, fn_args):
        global init_data
        init_data = fn(*fn_args)

    def get_init_params(self,manager:Manager):
        return []

    def getData(self, positions_with_zoom: np.ndarray) -> np.ndarray:
        assert len(positions_with_zoom.shape) == 2 and positions_with_zoom.shape[0] == 3
        res = None

        sample_fn = self.getSampleFN()

        res = sample_fn(positions_with_zoom,self._init_data)

        assert res.shape == positions_with_zoom.shape
        assert res.dtype == np.uint8

        return res

    def getSampleFN(self):
        pass
