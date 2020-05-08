import numpy as np

from source.mathutils import assertMultipleVec2d
from source.lat_lng import LatLng
from source.preprojections import LambertAzimuthalEqualArea, AbstractPreprojection


class ComplexLogProjection():
    def __init__(self,
                 center1: LatLng,
                 center2: LatLng,
                 smoothing_angle_radians: float,
                 preprojection: AbstractPreprojection = LambertAzimuthalEqualArea()):
        self.preprojection = preprojection  # is not centered around the center point
        self.center1 = preprojection(np.array([[center1.lat], [center1.lng]]))
        self.center2 = preprojection(np.array([[center2.lat], [center2.lng]]))
        self.smoothing_angle = smoothing_angle_radians
        self.midpoint = np.mean(np.concatenate([self.center1, self.center2], axis=1), axis=1)

    def __call__(self, latlng: np.ndarray) -> np.ndarray:
        assertMultipleVec2d(latlng)
        _ = self.preprojection(latlng)
