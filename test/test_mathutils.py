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

    def test_euclideanDistSquared(self):
        points = np.array([[0, 1], [0, 1]], dtype=float)
        point = np.array([[0], [0]], dtype=float)
        expected = np.array([0, 2], dtype=float)
        out = mathutils.euclideanDistSquared(points, point)
        np.testing.assert_almost_equal(out, expected)

    def test_euclideanDist(self):
        points = np.array([[0, 1], [0, 1]], dtype=float)
        point = np.array([[0], [0]], dtype=float)
        expected = np.array([0, math.sqrt(2)], dtype=float)
        out = mathutils.euclideanDist(points, point)
        np.testing.assert_almost_equal(out, expected)

    def test_createRotationMatrix(self):
        zeroRot = mathutils.createRotationMatrix(0)
        np.testing.assert_almost_equal(zeroRot, np.array([
            [1, 0],
            [0, 1]
        ]))

        piRot = mathutils.createRotationMatrix(math.pi)
        np.testing.assert_almost_equal(piRot, np.array([
            [-1, 0],
            [0, -1]
        ]))

        beforeRot = np.array([[0], [1]])
        afterRot = np.matmul(piRot, beforeRot)
        np.testing.assert_almost_equal(afterRot, np.array([[0], [-1]]))

    def test_normalizeAngles(self):
        data = np.array([0, 5.5 * math.pi, -1.5 * math.pi])
        expected = np.array([0, -.5 * math.pi, .5 * math.pi])
        np.testing.assert_almost_equal(mathutils.normalizeAngles(data), expected)
