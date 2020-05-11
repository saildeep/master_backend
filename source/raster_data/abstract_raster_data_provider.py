import abc
import numpy as np


class AbstractRasterDataProvider(abc.ABC):

    def getData(self, positions_with_zoom: np.ndarray) -> np.ndarray:
        assert len(positions_with_zoom.shape) == 2 and positions_with_zoom.shape[0] == 3
        res = self._sample(positions_with_zoom)
        assert res.shape == positions_with_zoom.shape
        assert res.dtype == np.uint8

        return res

    @abc.abstractmethod
    # gets x,y, zoomlevel and should equally sized RGB
    def _sample(self, positions_with_zoom: np.ndarray) -> np.ndarray:
        pass
