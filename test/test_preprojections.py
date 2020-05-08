import unittest
import numpy as np
from source import preprojections

input_data = np.transpose([
    [0, 0],
    [45, 0],
    [0, 45],
    [-45, 45]
])


class TestPreprojections(unittest.TestCase):

    def test_lambertEqualArea(self):
        projection = preprojections.LambertAzimuthalEqualArea()
        output_data = projection(input_data)
        np.testing.assert_almost_equal(output_data[:, 0], np.array([0, 0]))  # assert center has not moved
        offcenter_point = output_data[:, 1]
        self.assertTrue(offcenter_point[0] != 0 or offcenter_point[1] != 0)  # assert other point is of center

        desired_output = np.transpose([[0, 0],
                                       [0.7653668647301796, 0],
                                       [0, 0.7653668647301796],
                                       [-0.5773502691896257, 0.8164965809277259]])

        np.testing.assert_almost_equal(output_data, desired_output)

    def test_lambertEqualDistance(self):
        projection = preprojections.LambertAzimuthalEqualDistance()
        output_data = projection(input_data)
        np.testing.assert_almost_equal(output_data[:, 0], np.array([0, 0]))  # assert center has not moved
        offcenter_point = output_data[:, 1]
        self.assertTrue(offcenter_point[0] != 0 or offcenter_point[1] != 0)  # assert other point is of center

        desired_output = np.transpose([[0, 0],
                                       [0.7853981633974482, 0],
                                       [0, 0.7853981633974482],
                                       [-0.6045997880780726, 0.8550332201079093]])
        np.testing.assert_almost_equal(output_data, desired_output)
