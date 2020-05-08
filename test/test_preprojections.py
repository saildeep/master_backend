import unittest
import numpy as np
from source import preprojections


class TestPreprojections(unittest.TestCase):

    def test_lambertEqualArea(self):
        input_data = np.array([
            [0, 45], [0, 0]
        ])

        projection = preprojections.LambertAzimuthalEqualArea()
        output_data = projection(input_data)
        np.testing.assert_almost_equal(output_data[:, 0], np.array([0, 0]))  # assert center has not moved
        offcenter_point = output_data[:, 1]
        self.assertTrue(offcenter_point[0] != 0 or offcenter_point[1] != 0)  # assert other point is of center

    def test_lambertEqualDistance(self):
        input_data = np.array([
            [0, 45], [0, 0]
        ])

        projection = preprojections.LambertAzimuthalEqualDistance()
        output_data = projection(input_data)
        np.testing.assert_almost_equal(output_data[:, 0], np.array([0, 0]))  # assert center has not moved
        offcenter_point = output_data[:, 1]
        self.assertTrue(offcenter_point[0] != 0 or offcenter_point[1] != 0)  # assert other point is of center
