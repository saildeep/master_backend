import numpy as np
import math

from source.mathutils import \
    assertMultipleVec2d, \
    midpoint, \
    vectorAngles, \
    euclideanDistSquared, \
    createRotationMatrix, \
    euclideanDist, \
    complexLog, \
    complexExp
from source.lat_lng import LatLng
from source.preprojections import LambertAzimuthalEqualArea, AbstractPreprojection
from source.smoothing_functions import AbstractSmoothingFunction, NoSmoothingFunction
from source.zoomable_projection import ZoomableProjection


class ComplexLogProjection(ZoomableProjection):
    def __init__(self,
                 center1: LatLng,
                 center2: LatLng,
                 smoothing_angle_radians: float,
                 preprojection: AbstractPreprojection = LambertAzimuthalEqualArea(),
                 smoothing_function_type: AbstractSmoothingFunction.__class__ = NoSmoothingFunction):
        self.preprojection: AbstractPreprojection = preprojection  # is not centered around the center point
        self.center1: np.ndarray = preprojection(np.array([[center1.lat], [center1.lng]]))
        self.center2: np.ndarray = preprojection(np.array([[center2.lat], [center2.lng]]))
        self.smoothing_angle: float = smoothing_angle_radians
        self.midpoint: np.ndarray = midpoint(self.center1, self.center2)
        self.scale: float = (1.0 / euclideanDist(self.center1, self.midpoint))[0]

        self.theta1: float = math.pi - vectorAngles(self.center1 - self.midpoint)[0]
        self.theta2: float = math.pi - vectorAngles(self.center2 - self.midpoint)[0]

        self.smoothing_function: AbstractSmoothingFunction = smoothing_function_type(smoothing_angle_radians)

    def __call__(self, latlng: np.ndarray) -> np.ndarray:
        assertMultipleVec2d(latlng)
        projected = self.preprojection(latlng)
        dist_c1 = euclideanDistSquared(projected, self.center1)
        dist_c2 = euclideanDistSquared(projected, self.center2)

        selection_c1 = dist_c1 < dist_c2
        selection_c2 = dist_c1 >= dist_c2
        del dist_c1, dist_c2
        data_c1 = projected[:, selection_c1]
        data_c2 = projected[:, selection_c2]

        projected_c1 = self._single_forward(data_c1, self.center1, self.theta1, 1)
        projected_c2 = self._single_forward(data_c2, self.center2, self.theta2, -1)

        projected[:, selection_c1] = projected_c1
        projected[:, selection_c2] = projected_c2
        return projected

    def invert(self, xy: np.ndarray):
        assertMultipleVec2d(xy)
        selection_c1 = xy[0, :] < 0
        selection_c2 = xy[0, :] >= 0

        data_c1 = xy[:, selection_c1]
        data_c2 = xy[:, selection_c2]
        exp_c1 = self._single_backward(data_c1, self.center1, self.theta1, 1)
        exp_c2 = self._single_backward(data_c2, self.center2, self.theta2, -1)

        unprojected = np.zeros_like(xy)
        unprojected[:, selection_c1] = exp_c1
        unprojected[:, selection_c2] = exp_c2
        return self.preprojection.invert(unprojected)

    def _single_forward(self, points: np.ndarray, center: np.ndarray, theta: float, direction: int) -> np.ndarray:
        points -= center
        rotMat = createRotationMatrix(theta)
        points = np.matmul(rotMat, points)

        points *= self.scale
        points = complexLog(points)
        points = self.smoothing_function(points)

        points *= direction

        return points

    def _single_backward(self, points: np.ndarray, center: np.ndarray, theta: float, direction: int) -> np.ndarray:
        points /= direction
        points = self.smoothing_function.invert(points)
        points = complexExp(points)
        points /= self.scale

        rot_mat = createRotationMatrix(-1 * theta)
        points = np.matmul(rot_mat, points)

        points += center

        return points

    def getZoomLevel(self, pixel_data: np.ndarray, pixel_per_unit:float) -> np.ndarray:
        assertMultipleVec2d(pixel_data)
        pixel_data = pixel_data.copy()
        pixel_data = self.smoothing_function.invert(pixel_data)
        size_per_pixel_azimuth_units = np.exp(np.abs(pixel_data[0,:]))/pixel_per_unit
        size_per_pixel_latlng = (180/math.pi) * size_per_pixel_azimuth_units  / self.scale
        zoom = np.log2(size_per_pixel_latlng)+6
        return zoom
