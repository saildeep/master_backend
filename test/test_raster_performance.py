import math
import unittest

from source.complex_log_projection import ComplexLogProjection
from source.lat_lng import LatLng
from source.raster_data.osm_raster_data_provider import OSMRasterDataProvider
from source.raster_projector import RasterProjector, TargetSectionDescription
from source.smoothing_functions import DualCosSmoothingFunction, CosCutoffSmoothingFunction


class TestRasterPerformance(unittest.TestCase):
    konstanz = LatLng(47.711801, 9.084545)
    hoffeld = LatLng(48.735051, 9.181156)
    projection = ComplexLogProjection(konstanz, hoffeld, math.pi / 6,
                                      smoothing_function_type=CosCutoffSmoothingFunction)

    projector = RasterProjector(projection, OSMRasterDataProvider())

    def test_profile(self):

        trange = TargetSectionDescription(-math.pi * 2, math.pi * 2, 1600, -math.pi, math.pi, 200)
        d = self.projector.project(trange)

