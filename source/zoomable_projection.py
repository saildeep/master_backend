import abc
import numpy as np


class ZoomableProjection(abc.ABC):

    @abc.abstractmethod
    def __call__(self, data: np.ndarray) -> np.ndarray:
        pass

    @abc.abstractmethod
    def invert(self, data: np.ndarray) -> np.ndarray:
        pass

    @abc.abstractmethod
    def getZoomLevel(self, data: np.ndarray, pixel_per_unit: float) -> np.ndarray:
        pass


class IdentityProjection(ZoomableProjection):
    def __call__(self, data: np.ndarray) -> np.ndarray:
        return data

    def invert(self, data: np.ndarray) -> np.ndarray:
        return data

    def getZoomLevel(self, data: np.ndarray, pixel_per_unit: float) -> np.ndarray:
        return np.ones(data.shape[1])
