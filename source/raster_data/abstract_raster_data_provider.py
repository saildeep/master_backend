import abc

import numpy as np
from source.raster_data import tile_math
from multiprocessing import Pool, cpu_count



class AbstractRasterDataProvider(abc.ABC):

    def __init__(self):

        self.process_pool = Pool(processes=cpu_count(),initializer=self._init_process,initargs=self._get_init_params())

    def _init_process(self,* args):
        pass

    def _get_init_params(self):
        return []

    def getData(self, positions_with_zoom: np.ndarray) -> np.ndarray:
        assert len(positions_with_zoom.shape) == 2 and positions_with_zoom.shape[0] == 3

        min_chunk_size = 50
        tiles = tile_math.latlngZoomToXYZoomNP(positions_with_zoom)
        tiles_x = tiles[0,:].astype(int)
        tiles_y = tiles[1,:].astype(int)
        tiles_zoom = tiles[2,:].astype(int)


        cuts = np.arange(1,positions_with_zoom.shape[1]-2,min_chunk_size)
        parts = np.split(positions_with_zoom, cuts, axis=1)
        thread_results = self.process_pool.map(self._getSampleFN(),parts)


        res = np.concatenate(thread_results, axis=1)

        # res = self._sample(positions_with_zoom)
        assert res.shape == positions_with_zoom.shape
        assert res.dtype == np.uint8

        return res

    @abc.abstractmethod
    def _getSampleFN(self):
        pass

