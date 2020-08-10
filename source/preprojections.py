import abc
import numpy as np

from source import mathutils


# handles radiant conversion
class AbstractPreprojection(abc.ABC):

    def __call__(self, latlng: np.ndarray) -> np.ndarray:
        mathutils.assertMultipleVec2d(latlng)
        return mathutils.assertMultipleVec2d(self._forward(np.deg2rad(latlng)))

    def invert(self, xy: np.ndarray) -> np.ndarray:
        mathutils.assertMultipleVec2d(xy)
        return mathutils.assertMultipleVec2d(
            np.rad2deg(self._backward(xy))
        )

    @abc.abstractmethod
    def _forward(self, latlng_radians: np.ndarray) -> np.ndarray:
        pass

    @abc.abstractmethod
    def _backward(self, xy: np.ndarray) -> np.ndarray:
        pass

class IdentityPreprojection(AbstractPreprojection):

    def _forward(self, latlng_radians: np.ndarray) -> np.ndarray:
        return latlng_radians

    def _backward(self, xy: np.ndarray) -> np.ndarray:
        return xy


# implementation according to https://github.com/d3/d3-geo/blob/master/src/projection/azimuthal.js
class AbstractAzimutalProject(AbstractPreprojection):
    def _forward(self, latlng_radians: np.ndarray) -> np.ndarray:
        x = latlng_radians[0, :]
        y = latlng_radians[1, :]
        cx = np.cos(latlng_radians[0, :])
        cy = np.cos(latlng_radians[1, :])
        k = self._scale(cx * cy)
        return np.stack([k * cy * np.sin(x), k * np.sin(y)])

    def _backward(self, xy: np.ndarray) -> np.ndarray:
        x = xy[0, :]
        y = xy[1, :]
        z = np.sqrt(x * x + y * y)
        c = self._angle(z)
        sc = np.sin(c)
        cc = np.cos(c)
        res_lng = np.divide(y * sc, z, where=z != 0)
        res_lng[z == 0] = 0
        return np.stack([
            np.arctan2(x * sc, z * cc), np.arcsin(res_lng)], axis=0)

    @abc.abstractmethod
    def _scale(self, cxcy: np.ndarray) -> np.ndarray:
        pass

    @abc.abstractmethod
    def _angle(self, c: np.ndarray) -> np.ndarray:
        pass


class LambertAzimuthalEqualArea(AbstractAzimutalProject):

    def _scale(self, cxcy: np.ndarray) -> np.ndarray:
        return np.sqrt(2 / (1 + cxcy))

    def _angle(self, c: np.ndarray) -> np.ndarray:
        return 2 * np.arcsin(c / 2)


class LambertAzimuthalEqualDistance(AbstractAzimutalProject):

    def _scale(self, cxcy: np.ndarray) -> np.ndarray:
        c = np.arccos(cxcy)
        o = np.divide(c, np.sin(c), where=c != 0)
        o[c == 0] = 0
        return o

    def _angle(self, c: np.ndarray) -> np.ndarray:
        return c
