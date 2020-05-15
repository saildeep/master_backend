import abc

import numpy as np
from source.raster_data import tile_math
from multiprocessing import Pool, cpu_count


def getInitData():
    global init_data
    return init_data

def _runFN(fn, data):
    global init_data
    return fn(data, init_data)


class AbstractRasterDataProvider(abc.ABC):

    def __init__(self):
        self.process_pool = Pool(processes=cpu_count(), initializer=self._init_process,
                                 initargs=(self.init_process, self.get_init_params()))

    @abc.abstractmethod
    def init_process(self, *args):
        pass

    def _init_process(self, fn, fn_args):
        global init_data
        init_data = fn(*fn_args)

    def get_init_params(self):
        return []

    def getData(self, positions_with_zoom: np.ndarray) -> np.ndarray:
        assert len(positions_with_zoom.shape) == 2 and positions_with_zoom.shape[0] == 3

        min_chunk_size = 100
        tiles = tile_math.latlngZoomToXYZoomNP(positions_with_zoom)
        tiles_x = tiles[0, :].astype(int)
        tiles_y = tiles[1, :].astype(int)
        tiles_zoom = tiles[2, :].astype(int)

        cuts = np.arange(1, positions_with_zoom.shape[1] - 2, min_chunk_size)
        parts = np.split(positions_with_zoom, cuts, axis=1)


        thread_results = self.process_pool.map(self.getSampleFN(), parts)

        res = np.concatenate(thread_results, axis=1)

        # res = self._sample(positions_with_zoom)
        assert res.shape == positions_with_zoom.shape
        assert res.dtype == np.uint8

        return res

    def getSampleFN(self):
        pass
