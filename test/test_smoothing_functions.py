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

    def test_write_vis_curve(self):
        import matplotlib.pyplot as plt
        import  matplotlib as mpl
        fig,axs = plt.subplots(1,4,figsize=(5.8,2))


        for ax,angle in zip(axs.flat,[0,15,30,44.99]):

            sfdc = DualCosSmoothingFunction(angle * math.pi / 180.0)
            inv = np.linspace(-math.pi, math.pi, 400)

            ax.plot(inv * 180/math.pi, sfdc.scale(inv))
            ax.set_title("$\gamma={}°$".format(angle),fontsize=8)
            ax.grid(True)
            ax.set_xlim([-120,120])
            x_ticks = np.linspace(-90,90,5)
            ax.set_xticks(x_ticks)
            ax.set_xticklabels(list(map(lambda x:"{:.0f}°".format(x),x_ticks)))
            ax.set_ylim([0,1.2])

            y_ticks = np.linspace(0,1.0,6)
            ax.set_yticks(y_ticks)
            ax.set_yticklabels(list(map(lambda x: "{:.1f}".format(x), y_ticks)))

            ax.tick_params(axis='both', which='major', labelsize=6)
            ax.tick_params(axis='both', which='minor', labelsize=4)
        fig.tight_layout(rect=(0,0,1,.95))
        fig.suptitle("Smoothing function for different cutoff angle values $\gamma$",fontsize=10)
        fig.savefig('./vis_cutoff_angle.pdf')