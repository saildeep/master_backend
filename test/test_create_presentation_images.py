from unittest import TestCase

import math
import matplotlib.pyplot as plt


def save_plot(fig,name):
    fig.show()
    #fig.savefig(name + '.png',dpi=1000)


fig_w = 5
center_positions= [(2,1.5),(4,3)]
midpoint = ((center_positions[0][0] + center_positions[1][0])*.5,(center_positions[0][1] + center_positions[1][1])*.5)

center_distance = math.sqrt( (center_positions[0][0]- center_positions[1][0])**2 + (center_positions[0][1]- center_positions[1][1])**2 )

class TestCreatePresentationImages(TestCase):

    def test_create_circles(self):
        fig = plt.figure(
        #    figsize=(5,5)
        )

        ax = plt.gca()
        ax.set_aspect('equal')
        ax.set_xlim(0, 7)
        ax.set_ylim(0, 5)

        ax.scatter(list(map(lambda x:x[0],center_positions)),list(map(lambda x:x[1],center_positions)))

        for i,cp in enumerate(center_positions):
            x = cp[0]
            y = cp[1]
            ax.annotate("$~G^{}$".format(i+1), (x,y),va="top",ha='left')
        save_plot(fig,'only_points')

        ax.plot([center_positions[0][0], center_positions[1][0]], [center_positions[0][1], center_positions[1][1]],
                linestyle='dashed')
        ax.scatter([midpoint[0]],[midpoint[1]],color='black')
        ax.annotate("$~M$",midpoint,va="top",ha='left')
        save_plot(fig,'midpoint')


        ax.add_patch(plt.Circle(center_positions[0], center_distance/2, color='orange', alpha=0.5,zorder=-1))
        ax.add_patch(plt.Circle(center_positions[1], center_distance / 2, color='orange', alpha=0.5,zorder=-1))


        save_plot(fig,'circles')
