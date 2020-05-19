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
        self.use_mp = True

        if self.use_mp:
            self.process_pool = Pool(processes=int(cpu_count()), initializer=self._init_process,
                                 initargs=(self.init_process, self.get_init_params(manager)))
        else:
            self._init_process(self.init_process,self.get_init_params(None))

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
        if self.use_mp:
            min_chunk_size = 1000

            cuts = np.arange(1, positions_with_zoom.shape[1] - 2, min_chunk_size)
            parts = np.split(positions_with_zoom, cuts, axis=1)

            thread_results = self.process_pool.map(self.getSampleFN(), parts,10)

            res = np.concatenate(thread_results, axis=1)
        else:
            sample_fn = self.getSampleFN()
            res = sample_fn(positions_with_zoom)

        assert res.shape == positions_with_zoom.shape
        assert res.dtype == np.uint8

        return res

    def getSampleFN(self):
        pass
