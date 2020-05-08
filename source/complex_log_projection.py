from source.lat_lng import LatLng
from source.preprojections import LambertAzimuthalEqualArea, AbstractPreprojection


class ComplexLogProject():
    def __init__(self,
                 center1: LatLng,
                 center2: LatLng,
                 smoothing_angle_radians: float,
                 preprojection: AbstractPreprojection = LambertAzimuthalEqualArea):
        self.center1 = center1
        self.center2 = center2
        self.smoothing_angle = smoothing_angle_radians
        self.preprojection = preprojection
