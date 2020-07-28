from unittest import TestCase

import math

from source.complex_log_projection import ComplexLogProjection
from source.hard_coded_providers import get_providers
from source.lat_lng import LatLng
from source.raster_projector import RasterProjector, TargetSectionDescription
from source.smoothing_functions import DualCosSmoothingFunction
from PIL import Image

class CreateSampleImages(TestCase):
    def test_project_image_osm_wide(self):
        prov = get_providers()
        for angle in [0,10,20,30,40]:
            frankfurt_a_m = LatLng(50.115822, 8.702537)
            leipzig = LatLng(51.348419, 12.370946)  #
            projection = ComplexLogProjection(frankfurt_a_m, leipzig, math.radians(angle),
                                              smoothing_function_type=DualCosSmoothingFunction)
            projector = RasterProjector(projection, prov['transparent'])
            trange = TargetSectionDescription(-math.pi * 3, math.pi * 3, 2000, -math.pi, math.pi, 500)
            d = projector.project(trange)
            im = Image.fromarray(d)
            filename = "sample-angle-" + str(angle)+".png"
            im.save(filename)
            print("Finished " + filename)


