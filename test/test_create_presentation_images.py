from unittest import TestCase

import math
import matplotlib.pyplot as plt
import os

import numpy as np
from source.smoothing_functions import DualCosSmoothingFunction


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

    def add_modified_range_circles(self,ax,angle=30):
        smoothing = DualCosSmoothingFunction(math.radians(angle))
        r = center_distance *.5
        diff_vec =  np.array(center_positions[1]) - np.array(center_positions[0])
        direction_angular = math.atan2(diff_vec[1],diff_vec[0])

        for center, direction_angular in zip(center_positions,[direction_angular,direction_angular+math.pi]):
            polygon = []
            for angle in np.linspace(0,math.pi * 2,200,endpoint=False):
                r_mod = (r / smoothing.scale(np.array([angle - direction_angular])))[0]
                x = center[0] + math.cos(angle) * r_mod
                y = center[1] + math.sin(angle) * r_mod
                polygon.append((x,y))

            polygon = np.array(polygon)

            ax.add_patch(plt.Polygon(np.array(polygon),color='blue',alpha=.5))




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

        self.add_modified_range_circles(ax)

        save_plot(fig,'circles')
