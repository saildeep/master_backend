import numpy as np
import abc
import math

from source.mathutils import assertMultipleVec2d, normalizeAngles


class AbstractSmoothingFunction(abc.ABC):
    def __init__(self, cutoff_angle: float):
        assert cutoff_angle >= 0
        self.cutoff_angle = cutoff_angle

    @abc.abstractmethod
    def __call__(self, data: np.ndarray):
        pass

    @abc.abstractmethod
    def invert(self, data: np.ndarray):
        pass


class NoSmoothingFunction(AbstractSmoothingFunction):

    def __call__(self, data: np.ndarray):
        return data

    def invert(self, data: np.ndarray):
        return data


class AngleScalingSmoothingFunction(AbstractSmoothingFunction):

    def __call__(self, data: np.ndarray):
        assertMultipleVec2d(data)
        current_angle = data[1, :]
        scaled = np.log(np.abs(self.scale(current_angle)))
        data[0, :] += scaled
        return data

    def invert(self, data: np.ndarray):
        assertMultipleVec2d(data)
        current_angle = data[1, :]
        scaled = np.log(np.abs(self.scale(current_angle)))
        data[0, :] -= scaled
        return data

    @abc.abstractmethod
    def scale(self, data: np.ndarray):
        pass


class CosCutoffSmoothingFunction(AngleScalingSmoothingFunction):

    def scale(self, data: np.ndarray):
        return np.maximum(np.cos(data), np.cos(self.cutoff_angle))


class DualCosSmoothingFunction(AngleScalingSmoothingFunction):

    def scale(self, data: np.ndarray):
        cutoff_value = np.cos(self.cutoff_angle)
        cuton_position = math.pi - self.cutoff_angle
        normed_angles = np.abs(normalizeAngles(data))
        selection_incutoff = normed_angles < self.cutoff_angle
        selection_outerspace = normed_angles > 2 * self.cutoff_angle
        selection_inbetween = np.invert(np.logical_or(selection_incutoff, selection_outerspace))

        scale = np.zeros_like(data)
        scale[selection_incutoff] = np.cos(normed_angles[selection_incutoff])
        scale[selection_outerspace] = np.cos(2 * self.cutoff_angle)
        scale[selection_inbetween] = 2 * cutoff_value + np.cos(
            cuton_position + (normed_angles[selection_inbetween] - self.cutoff_angle))

        return scale

        pass
