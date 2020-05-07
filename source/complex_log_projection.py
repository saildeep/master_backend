from source.lat_lng import LatLng


class ComplexLogProject():
    def __init__(self, center1: LatLng, center2: LatLng, smoothing_angle_radians: float):
        self.center1 = center1
        self.center2 = center2
        self.smoothing_angle = smoothing_angle_radians
