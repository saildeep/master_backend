import abc

import numpy as np
import threading
from multiprocessing import Pool
import random
import queue


class AbstractRasterDataProvider(abc.ABC):

    def __init__(self):

        self.process_pool = Pool(processes=4,initializer=self._init_process,initargs=self._get_init_params())

    def _init_process(self,* args):
        pass

    def _get_init_params(self):
        return []

    def getData(self, positions_with_zoom: np.ndarray) -> np.ndarray:
        assert len(positions_with_zoom.shape) == 2 and positions_with_zoom.shape[0] == 3

        min_chunk_size = 50
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

