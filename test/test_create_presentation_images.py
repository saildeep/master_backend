from unittest import TestCase

import math
import matplotlib.pyplot as plt


def save_plot(fig,name):
    fig.show()
    #fig.savefig(name + '.png',dpi=1000)


fig_w = 5
center_positions= [(2,1),(4,3)]
midpoint = ((center_positions[0][0] + center_positions[1][0])*.5,(center_positions[0][1] + center_positions[1][1])*.5)

center_distance = math.sqrt( (center_positions[0][0]- center_positions[1][0])**2 + (center_positions[0][1]- center_positions[1][1])**2 )

class TestCreatePresentationImages(TestCase):

    def test_create_circles(self):
        fig = plt.figure(figsize=(5,5))

        ax = plt.gca()
        ax.set_xlim(0, 8)
        ax.set_ylim(0, 8)

        ax.scatter(list(map(lambda x:x[0],center_positions)),list(map(lambda x:x[1],center_positions)))

        for i,cp in enumerate(center_positions):
            x = cp[0]
            y = cp[1]
            ax.annotate("$G^{}$".format(i+1), (x,y),va="top",ha='left')

        ax.scatter([midpoint[0]],[midpoint[1]])
        ax.annotate("$M$",midpoint,va="top",ha='left')

        ax.add_patch(plt.Circle(center_positions[0], center_distance/2, color='orange', alpha=0.5))
        ax.add_patch(plt.Circle(center_positions[1], center_distance / 2, color='orange', alpha=0.5))

        ax.plot([center_positions[0][0],center_positions[1][0]],[center_positions[0][1],center_positions[1][1]],linestyle='dashed')

        save_plot(fig,'circles')
