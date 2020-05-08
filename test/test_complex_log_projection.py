import unittest
import math

from source.complex_log_projection import ComplexLogProjection
from source.lat_lng import LatLng


class TestComplexLogProjection(unittest.TestCase):
    def test_init(self):
        ComplexLogProjection(LatLng(0, 0), LatLng(10, 0), math.pi / 4)
