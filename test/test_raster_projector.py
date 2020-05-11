import unittest

from source.raster_data.function_raster_data_provider import CosSinRasterDataProvider
from source.raster_projector import RasterProjector, TargetSectionDescription
from source.zoomable_projection import IdentityProjection

import math


class TestRasterProjector(unittest.TestCase):
    def test_grid(self):
        projector = RasterProjector(IdentityProjection(), CosSinRasterDataProvider())
        trange = TargetSectionDescription(-1, 1, 3, -1, 1, 3)
        grid = projector._build_grid(trange)
        assert len(grid.shape) == 2 and grid.shape[1] == 3 * 3

    def test_project(self):
        projector = RasterProjector(IdentityProjection(), CosSinRasterDataProvider())
        trange = TargetSectionDescription(0, 2 * math.pi, 200, -1, 1, 100)
        d = projector.project(trange)

        assert d.shape[0] == trange.ysteps and d.shape[1] == trange.xsteps
        k = d[0, 50, 0]
        assert k == 127 and k == d[0, 0, 0]

        # import matplotlib.pyplot as plt
        # plt.imshow(d)
        # plt.show()

        pass
