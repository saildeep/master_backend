import unittest

from source.complex_log_projection import ComplexLogProjection
from source.lat_lng import LatLng
from source.raster_data.function_raster_data_provider import CosSinRasterDataProvider
from source.raster_data.osm_raster_data_provider import OSMRasterDataProvider
from source.raster_projector import RasterProjector, TargetSectionDescription
from source.smoothing_functions import DualCosSmoothingFunction, CosCutoffSmoothingFunction
from source.zoomable_projection import IdentityProjection

from logging import basicConfig, INFO

basicConfig(level=INFO)
import math


class TestRasterProjector(unittest.TestCase):
    def test_grid(self):
        projector = RasterProjector(IdentityProjection(), CosSinRasterDataProvider())
        trange = TargetSectionDescription(-1, 1, 3, -1, 1, 3)
        grid = projector.build_grid(trange)
        assert len(grid.shape) == 2 and grid.shape[1] == 3 * 3

    def test_project(self):
        projector = RasterProjector(IdentityProjection(), CosSinRasterDataProvider())
        trange = TargetSectionDescription(0, 2 * math.pi, 200, -1, 1, 100)
        d = projector.project(trange)

        assert d.shape[0] == trange.ysteps and d.shape[1] == trange.xsteps

    def project_image(self):
        projection = ComplexLogProjection(LatLng(0, 0), LatLng(10, 10), math.pi / 4)
        projector = RasterProjector(projection, CosSinRasterDataProvider())
        trange = TargetSectionDescription(-1, 1, 500, -1, 1, 300)
        d = projector.project(trange)

        import matplotlib.pyplot as plt
        plt.imshow(d)
        plt.show()

    def test_project_image_osm(self):
        konstanz = LatLng(47.711801, 9.084545)
        hoffeld = LatLng(48.735051, 9.181156)
        projection = ComplexLogProjection(konstanz, hoffeld, math.pi / 6,
                                          smoothing_function_type=DualCosSmoothingFunction)
        projector = RasterProjector(projection, OSMRasterDataProvider())
        trange = TargetSectionDescription(-math.pi * 2, math.pi * 2, 500, -math.pi, math.pi, 250)
        d = projector.project(trange)

        import matplotlib.pyplot as plt
        plt.imshow(d)
        plt.show()

    def test_project_image_osm_small(self):
        konstanz = LatLng(47.711801, 9.084545)
        sealive = LatLng(47.656846, 9.179489)  # sealive
        projection = ComplexLogProjection(konstanz, sealive, math.pi / 6,
                                          smoothing_function_type=CosCutoffSmoothingFunction)
        projector = RasterProjector(projection, OSMRasterDataProvider())
        trange = TargetSectionDescription(-math.pi * 2, math.pi * 2, 500, -math.pi, math.pi, 250)
        d = projector.project(trange)

        import matplotlib.pyplot as plt
        plt.imshow(d)
        plt.show()

    def test_project_image_osm_wide(self):
        konstanz = LatLng(47.711801, 9.084545)
        moscow = LatLng(55.712998, 37.627815)
        projection = ComplexLogProjection(konstanz, moscow, math.pi / 6,
                                          smoothing_function_type=CosCutoffSmoothingFunction)
        projector = RasterProjector(projection, OSMRasterDataProvider())
        trange = TargetSectionDescription(-math.pi * 4, math.pi * 4, 2000, -math.pi, math.pi, 500)
        d = projector.project(trange)

        import matplotlib.pyplot as plt
        plt.imshow(d)
        plt.show()

    def test_vis_zoomLevel(self):
        projection1 = ComplexLogProjection(LatLng(0, 0), LatLng(10, 10), math.pi / 4)
        projection2 = ComplexLogProjection(LatLng(-10, -10), LatLng(10, 10), math.pi / 4)
        projector = RasterProjector(projection1, OSMRasterDataProvider())
        grid = projector.build_grid(TargetSectionDescription(-4, 4, 400, -2, 2, 200))
        zoom = projection1.getZoomLevel(grid, 100)
        import matplotlib.pyplot as plt
        plt.imshow(zoom.reshape(200, 400))
        plt.colorbar()
        plt.show()
