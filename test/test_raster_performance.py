
import math
import unittest

from source.complex_log_projection import ComplexLogProjection
from source.lat_lng import LatLng
from source.raster_data.osm_raster_data_provider import OSMRasterDataProvider
from source.raster_projector import RasterProjector, TargetSectionDescription
from source.smoothing_functions import DualCosSmoothingFunction, CosCutoffSmoothingFunction
from test.raster_data import dummy_resolver


class TestRasterPerformance(unittest.TestCase):
    konstanz = LatLng(47.711801, 9.084545)
    hoffeld = LatLng(48.735051, 9.181156)
    data_provider =  OSMRasterDataProvider(dummy_resolver.dummy_resolver)

    def test_profile(self):
        projection = ComplexLogProjection(self.konstanz, self.hoffeld, math.pi / 6,
                                          smoothing_function_type=CosCutoffSmoothingFunction)

        projector = RasterProjector(projection, self.data_provider)
        trange = TargetSectionDescription(-math.pi * 2, math.pi * 2, 1600, -math.pi, math.pi, 200)
        d = projector.project(trange)


    def test_profile_close(self):

        t2 = LatLng(47.656846,9.179489) # sealive
        projection = ComplexLogProjection(self.konstanz, t2, math.pi / 6,
                                          smoothing_function_type=CosCutoffSmoothingFunction)

        projector = RasterProjector(projection, self.data_provider)
        trange = TargetSectionDescription(-math.pi * 2, math.pi * 2, 1600, -math.pi, math.pi, 200)
        d = projector.project(trange)
