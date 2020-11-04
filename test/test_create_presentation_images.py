from unittest import TestCase

import math
import matplotlib.pyplot as plt
import os


def save_plot(fig,name):

    folder = os.path.join('.','presentation')
    if not os.path.isdir(folder):
        os.mkdir(folder)

    fig.savefig(os.path.join(folder,name+'.png'),dpi=1000)


fig_w = 5
center_positions= [(2,1.5),(4,3)]
route = [center_positions[0],(2.2,2.5),(3.5,2.4),center_positions[1]]

midpoint = ((center_positions[0][0] + center_positions[1][0])*.5,(center_positions[0][1] + center_positions[1][1])*.5)

center_distance = math.sqrt( (center_positions[0][0]- center_positions[1][0])**2 + (center_positions[0][1]- center_positions[1][1])**2 )

class TestCreatePresentationImages(TestCase):




    def add_centers(self,ax):
        ax.scatter(list(map(lambda x: x[0], center_positions)), list(map(lambda x: x[1], center_positions)))

        for i, cp in enumerate(center_positions):
            x = cp[0]
            y = cp[1]
            ax.annotate("$~G^{}$".format(i + 1), (x, y), va="top", ha='left')


    def add_midline(self,ax):
        ax.plot([center_positions[0][0], center_positions[1][0]], [center_positions[0][1], center_positions[1][1]],
                linestyle='dashed')
        ax.scatter([midpoint[0]], [midpoint[1]], color='black')
        ax.annotate("$~M$", midpoint, va="top", ha='left')

    def add_range_circles(self,ax):
        ax.add_patch(plt.Circle(center_positions[0], center_distance / 2, color='orange', alpha=0.5, zorder=-1))
        ax.add_patch(plt.Circle(center_positions[1], center_distance / 2, color='orange', alpha=0.5, zorder=-1))

    def add_route(self,ax):

        x = []
        y = []
        for route_element in route:
            x.append(route_element[0])
            y.append(route_element[1])

        ax.plot(x,y,color='red')

    def test_create_circles(self):
        fig = plt.figure(
        #    figsize=(5,5)
        )

        ax = plt.gca()
        ax.set_aspect('equal')
        ax.set_xlim(0, 7)
        ax.set_ylim(0, 5)


        self.add_centers(ax)

        save_plot(fig,'only_points')

        self.add_route(ax)

        save_plot(fig,'route')


        self.add_midline(ax)




        save_plot(fig,'midpoint')

        self.add_range_circles(ax)

        save_plot(fig,'circles')
