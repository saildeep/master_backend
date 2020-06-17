import abc
from typing import Optional

import numpy as np


class AbstractRasterDataProvider(abc.ABC):

    def __init__(self):
        self._init_data = self.init_process(*self.get_init_params(None))

    @abc.abstractmethod
    def init_process(self, *args):
        pass

    def get_init_params(self, manager: Optional[object]):
        return []

    def getData(self, positions_with_zoom: np.ndarray) -> np.ndarray:
        assert len(positions_with_zoom.shape) == 2 and positions_with_zoom.shape[0] == 3

        sample_fn = self.getSampleFN()

        res = sample_fn(positions_with_zoom, self._init_data)

        assert res.shape == (3,positions_with_zoom.shape[1]) or res.shape == (4,positions_with_zoom.shape[1])
        assert res.dtype == np.uint8

        return res

    @abc.abstractmethod
    def getSampleFN(self):
        pass
