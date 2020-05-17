import unittest
import math
import numpy as np
from source.complex_log_projection import ComplexLogProjection
from source.lat_lng import LatLng


class TestComplexLogProjection(unittest.TestCase):
    def test_init(self):
        ComplexLogProjection(LatLng(0, 0), LatLng(10, 10), math.pi / 4)

    def test_loop(self):
        projection = ComplexLogProjection(LatLng(0, 0), LatLng(10, 10), math.pi / 4)
        # only small slice where no stitching was used
        data = np.array([
            [1, 9],
            [1, 9]
        ])
        res = projection(data.copy())
        returned = projection.invert(res.copy())
        np.testing.assert_almost_equal(returned, data)
        pass

    def test_single_loop(self):
        data = np.array([
            [0, 1, 0, 2],
            [1, 0, 3, 4]
        ], dtype=float)
        projection = ComplexLogProjection(LatLng(0, 0), LatLng(10, 10), math.pi / 4)
        center = np.array([[5], [6]], dtype=float)
        projected = projection._single_forward(data.copy(), center, 1, 1)
        back = projection._single_backward(projected, center, 1, 1)
        np.testing.assert_almost_equal(back, data)

    def test_single_example(self):
        projection = ComplexLogProjection(LatLng(0, 0), LatLng(10, 10), math.pi / 4)
        data = np.array([
            [1, 45, 0, -45],
            [1, 0, 45, 45]
        ])
        center = np.array([[0], [0]])
        projection._single_forward(data, center, math.pi, 1)

    def test_complete(self):
        projection = ComplexLogProjection(LatLng(0, 0), LatLng(10, 10), math.pi / 4)
        data = np.array([
            [1, 45, 0, -45],
            [1, 0, 45, 45]
        ])

        reference = np.transpose(np.array([[-1.6044065604314688, -0.007577958547331141],
                                           [-1.6165580696347939, -2.061643517294472],
                                           [-1.6112081515800694, 2.0798741549084134],
                                           [-2.083894545839403, 1.5008744404655734]]))
        projected = projection(data)
        np.testing.assert_almost_equal(projected, reference)
        pass

    def testZoomLevel(self):
        projection1 = ComplexLogProjection(LatLng(0, 0), LatLng(10, 10), math.pi / 4)

        projection2 = ComplexLogProjection(LatLng(-10, -10), LatLng(10, 10), math.pi / 4)
        data = np.array([[-1, -2, 1, 2], [1, 1, 1, 1]])
        # expected = np.array([np.exp(1), np.exp(2), np.exp(1), np.exp(2)])
        r1 = projection1.getZoomLevel(data,1)
        r2 = projection2.getZoomLevel(data,1)
        pass
        # TODO think about values



