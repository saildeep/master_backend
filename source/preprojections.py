import abc
import numpy as np

from source import mathutils


class AbstractPreprojection(abc.ABC):

    def __call__(self, latlng: np.ndarray) -> np.ndarray:
        mathutils.assertMultipleVec2d(latlng)
        return self._forward(latlng)

    def invert(self, xy: np.ndarray) -> np.ndarray:
        mathutils.assertMultipleVec2d(xy)
        return self._backward(xy)

    @abc.abstractmethod
    def _forward(self, latlng: np.ndarray) -> np.ndarray:
        pass

    @abc.abstractmethod
    def _backward(self, xy: np.ndarray) -> np.ndarray:
        pass
