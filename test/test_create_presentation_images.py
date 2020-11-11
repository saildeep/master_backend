from unittest import TestCase

import math
import matplotlib.pyplot as plt
import os

import numpy as np
from source.smoothing_functions import DualCosSmoothingFunction
import pickle


def save_plot(fig,name):

    folder = os.path.join('.','presentation')
    if not os.path.isdir(folder):
        os.mkdir(folder)
    fig.tight_layout()
    fig.savefig(os.path.join(folder,name+'.png'),dpi=500)


fig_h = 5
center_positions= [(2,1.5),(4,3)]
route = [center_positions[0],(2.2,2.5),(3.5,2.4),center_positions[1]]

midpoint = ((center_positions[0][0] + center_positions[1][0])*.5,(center_positions[0][1] + center_positions[1][1])*.5)

center_distance = math.sqrt( (center_positions[0][0]- center_positions[1][0])**2 + (center_positions[0][1]- center_positions[1][1])**2 )



displayable_area_style={
    "color":'blue',
    "alpha":0.3,
    "zorder":-1,
}

center_point_color = "orange"
midpoint_color = "green"
midline_style = {"color":"cyan","linestyle":"dashed"}
route_color="red"






class TestCreatePresentationImages(TestCase):




    def add_centers(self,ax):
        ax.scatter(list(map(lambda x: x[0], center_positions)), list(map(lambda x: x[1], center_positions)),color=center_point_color)

        for i, cp in enumerate(center_positions):
            x = cp[0]
            y = cp[1]
            ax.annotate("$~G^{}$".format(i + 1), (x, y), va="top", ha='left',color=center_point_color)


    def add_midline(self,ax):
        ax.plot([center_positions[0][0], center_positions[1][0]], [center_positions[0][1], center_positions[1][1]],
                **midline_style)
        ax.scatter([midpoint[0]], [midpoint[1]], color=midpoint_color)
        ax.annotate("$~M$", midpoint,color=midpoint_color, va="top", ha='left')

    def add_range_circles(self,ax):
        ax.add_patch(plt.Circle(center_positions[0], center_distance / 2, **displayable_area_style))
        ax.add_patch(plt.Circle(center_positions[1], center_distance / 2, **displayable_area_style))

    def add_modified_range_circles(self,ax,angle=30):
        smoothing = DualCosSmoothingFunction(math.radians(angle))
        r = center_distance *.5
        diff_vec =  np.array(center_positions[1]) - np.array(center_positions[0])
        direction_angular = math.atan2(diff_vec[1],diff_vec[0])

        for center, direction_angular in zip(center_positions,[direction_angular,direction_angular+math.pi]):
            polygon = self.get_modified_range_polygon_outline(angle,direction_angular,center,r)


            ax.add_patch(plt.Polygon(np.array(polygon),**displayable_area_style))


    def get_modified_range_polygon_outline(self,angle,angle_offset=0,center=[0,0],r=1.0):
        smoothing = DualCosSmoothingFunction(math.radians(angle))

        polygon = []
        for angle in np.linspace(0, math.pi * 2, 200, endpoint=False):
            r_mod = (r / smoothing.scale(np.array([angle-angle_offset ])))[0]
            x = center[0] + math.cos(angle) * r_mod
            y = center[1] + math.sin(angle) * r_mod
            polygon.append((x, y))

        polygon = np.array(polygon)
        return polygon



    def add_route(self,ax):

        x = []
        y = []
        for route_element in route:
            x.append(route_element[0])
            y.append(route_element[1])

        ax.plot(x,y,color='red')

    def get_new_fig(self):
        fig = plt.figure(figsize=(fig_h,fig_h))

        ax = plt.gca()
        ax.set_aspect('equal')
        ax.set_xlim(0, 7)
        ax.set_ylim(0, 5)

        return fig,ax

    def test_create_route(self):

        fig,ax = self.get_new_fig()

        self.add_centers(ax)

        self.add_route(ax)

        save_plot(fig,'route')





    def test_create_midpoint(self):

        fig, ax = self.get_new_fig()
        self.add_centers(ax)
        #self.add_route(ax)
        self.add_midline(ax)
        save_plot(fig, 'midpoint')

    def test_create_circles(self):

        fig, ax = self.get_new_fig()
        self.add_centers(ax)
        #self.add_route(ax)
        self.add_midline(ax)
        self.add_modified_range_circles(ax, angle=0)
        save_plot(fig, 'circles')

    def test_create_circles_affine(self):
        fig,axs = plt.subplots(1,3,figsize=(fig_h*1.8,fig_h))
        ax = axs[0]
        ax.set_aspect('equal')
        self.add_centers(ax)
        # self.add_route(ax)
        self.add_midline(ax)
        self.add_modified_range_circles(ax, angle=0)

        for i,ax in zip([0,1],[axs[1],axs[2]]):
            ax.set_aspect('equal')
            ax.scatter(0,0,color=center_point_color)
            ax.annotate("$~G^{}$".format(i + 1), (0, 0), va="bottom", ha='right',color=center_point_color)
            ax.scatter(1,0,color=midpoint_color)
            ax.annotate("$M$",(1,0), va="bottom", ha='right',color=midpoint_color)
            ax.add_patch(plt.Circle((0,0), 1, **displayable_area_style))
            ax.plot([0,1],[0,0],**midline_style)


        save_plot(fig,'circles_affine')

    def test_create_circles_affine_smoothed(self):
        fig, axs = plt.subplots(1, 3, figsize=(fig_h * 1.8, fig_h))
        ax = axs[0]
        ax.set_aspect('equal')
        self.add_centers(ax)
        # self.add_route(ax)
        self.add_midline(ax)
        angle = 30
        self.add_modified_range_circles(ax, angle=angle)



        for i, ax in zip([0, 1], [axs[1], axs[2]]):
            ax.set_aspect('equal')
            ax.scatter(0, 0, color=center_point_color)
            ax.annotate("$~G^{}$".format(i + 1), (0, 0), va="bottom", ha='right', color=center_point_color)
            ax.scatter(1, 0, color=midpoint_color)
            ax.annotate("$M$", (1, 0), va="bottom", ha='right', color=midpoint_color)
            polygon = self.get_modified_range_polygon_outline(angle)
            ax.add_patch(plt.Polygon(np.array(polygon), **displayable_area_style))

            ax.plot([0, 1], [0, 0], **midline_style)

        save_plot(fig, 'circles_affine_smoothed')

    def test_create_smoothed_circles(self):

        fig, ax = self.get_new_fig()
        self.add_centers(ax)
        #self.add_route(ax)
        self.add_midline(ax)
        self.add_modified_range_circles(ax, angle=30)
        save_plot(fig, 'circles_smoothed')