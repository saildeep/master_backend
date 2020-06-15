import unittest
import math
import numpy as np
from source.smoothing_functions import DualCosSmoothingFunction


class TestDualCosSmoothingFunction(unittest.TestCase):
    def test_scale(self):
        sf = DualCosSmoothingFunction(math.pi / 4)
        data = np.array(
            [0, .2 * math.pi, .25 * math.pi, -.25 * math.pi, 0.75 * math.pi])
        expected = np.array(
            [1, np.cos(.2 * math.pi), np.cos(.25 * math.pi), np.cos(.25 * math.pi), np.cos(.5 * math.pi)])
        res = sf.scale(data)
        np.testing.assert_almost_equal(res, expected)

    def test_vis_curve(self):
        import matplotlib.pyplot as plt
        sfdc = DualCosSmoothingFunction(math.pi/6)
        inv = np.linspace(-math.pi,math.pi,400)

        plt.plot(inv,sfdc.scale(inv))
        plt.show()