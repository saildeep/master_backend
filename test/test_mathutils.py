import unittest
import numpy as np
import source.mathutils as mathutils
import math


class TestMathutils(unittest.TestCase):

    def test_complexLog(self):
        input_data = np.array([
            [1, 0, 0], [0, 2, -1]
        ])
        expected_data = np.array([
            [math.log(1), math.log(2), math.log(1)],
            [0, math.pi / 2, -math.pi / 2]
        ])

        output_data = mathutils.complexLog(input_data)
        self.assertEqual(output_data.shape, input_data.shape)
        np.testing.assert_almost_equal(output_data, expected_data)

    def test_complexLogZero(self):
        np.testing.assert_almost_equal(mathutils.complexLog(np.array([[0], [0]])), np.array([[0], [0]]))

    def test_complexExp(self):
        input_data = np.array([
            [1, 0, 0], [0, 2, -1]
        ])
        # only do a cycle test for the provided values
        output_data = mathutils.complexExp(mathutils.complexLog(input_data))
        self.assertEqual(output_data.shape, input_data.shape)
        np.testing.assert_almost_equal(output_data, input_data)

    def test_midpoint(self):
        p1_in = np.array([[0], [0]])
        p2_in = np.array([[1], [2]])
        expected = np.array([[.5], [1]])
        output = mathutils.midpoint(p1_in, p2_in)
        np.testing.assert_almost_equal(output, expected)

    def test_vectorAngles(self):
        input_data = np.array([
            [1, 0, 1],
            [0, 1, 1]
        ])
        expected = np.array([0, math.pi / 2, math.pi / 4])
        output_data = mathutils.vectorAngles(input_data)
        np.testing.assert_almost_equal(output_data, expected)
