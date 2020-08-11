from unittest import TestCase

import math

from source.complex_log_projection import ComplexLogProjection
from source.hard_coded_providers import get_providers
from source.lat_lng import LatLng
from source.preprojections import IdentityPreprojection
from source.raster_data.function_raster_data_provider import CosSinRasterDataProvider
from source.raster_projector import RasterProjector, TargetSectionDescription
from source.smoothing_functions import DualCosSmoothingFunction
from source.mathutils import euclideanDist, anglesBetween, triangleArea
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize,LogNorm

class CreateSampleImages(TestCase):
    def test_project_image_angles(self):
        prov = get_providers()
        trange = TargetSectionDescription(-math.pi * 2, math.pi * 2, 4000, -math.pi/2, math.pi/2, 1000)
        #frankfurt_a_m = LatLng(50.115822, 8.702537)
        halle = LatLng(51.506136,11.964422)

        leipzig = LatLng(51.348419, 12.370946)  #
        for angle in [0,15,30,45]:

            projection = ComplexLogProjection(halle, leipzig, math.radians(angle),
                                              smoothing_function_type=DualCosSmoothingFunction)
            projector_transparent = RasterProjector(projection, prov['transparent'])
            projector_mapbox = RasterProjector(projection, prov['mapbox'])

            d_trans =  Image.fromarray(projector_transparent.project(trange))
            d_mapbox = Image.fromarray(projector_mapbox.project(trange))

            im = Image.alpha_composite(d_mapbox,d_trans)
            filename = "sample-angle-" + str(angle)+".png"
            im.save(filename)
            print(filename)

    def test_project_image_distances(self):
            prov = get_providers()
            trange = TargetSectionDescription(-math.pi * 2, math.pi * 2, 4000, -math.pi, math.pi, 2000)
            #frankfurt_a_m = LatLng(50.115822, 8.702537)
            angle = 30
            hamburg = LatLng(53.559988,9.982358)
            hamburg_elbbruecken = LatLng(53.535251,10.020135)
            lueneburg = LatLng(53.245280,10.408478)
            hannover = LatLng(52.370487,9.724743)
            fulda = LatLng(50.527068,9.684608)
            stockach = LatLng(47.847596,9.007671)
            for i,to in enumerate([ hamburg_elbbruecken,lueneburg,hannover,fulda,stockach]):

                projection = ComplexLogProjection(hamburg, to, math.radians(angle),
                                                  smoothing_function_type=DualCosSmoothingFunction)
                projector_transparent = RasterProjector(projection, prov['transparent'])
                projector_mapbox = RasterProjector(projection, prov['mapbox'])

                d_trans =  Image.fromarray(projector_transparent.project(trange))
                d_mapbox = Image.fromarray(projector_mapbox.project(trange))

                im = Image.alpha_composite(d_mapbox,d_trans)
                dist = int(hamburg.distanceTo(to))
                filename = "sample-distance-" + str(dist)+".png"
                im.save(filename)

                print("Finished " + filename + " with distance " + str(dist))

    def test_distance_scaling(self):

        fs = (7,7)
        fig_distance,axes_distance = plt.subplots(2,2,num=0,figsize=fs)
        fig_angle,axes_angle =plt.subplots(2,2,num=1,figsize=fs)
        fig_area,axes_area = plt.subplots(2,2,num=2,figsize=fs)

        limb_length_max = 0.001

        for i,angle in enumerate([0,15,30,45]):
            projection = ComplexLogProjection(LatLng(-1,0),LatLng(1,0),math.radians(angle),smoothing_function_type=DualCosSmoothingFunction,preprojection=IdentityPreprojection())
            trange = TargetSectionDescription(-2,2,2000,-2,2,2000)
            extent = [trange.xmin,trange.xmax,trange.ymin,trange.ymax]
            rp = RasterProjector(projection,CosSinRasterDataProvider)
            grid = rp.build_grid(trange)
            #offset = np.stack([          np.ones((grid.shape[1],))*0.01,            np.ones((grid.shape[1],))*0],axis=0)
            offset = np.random.uniform(-limb_length_max/math.sqrt(2),limb_length_max/math.sqrt(2),grid.shape)
            offset_2 =  np.stack([offset[1,:],-offset[0,:] ],axis=0)
            #offset_2 = np.random.uniform(-0.01,0.01,grid.shape)
            grid_offset = grid+ offset
            grid_offset_2 = grid + offset_2
            euclid = euclideanDist(grid,grid_offset)
            grid_projected = projection(grid)
            grid_offset_projected = projection(grid_offset)
            grid_offset_projected_2 = projection(grid_offset_2)
            projected_euclid = euclideanDist(grid_projected,grid_offset_projected)
            ratio = projected_euclid / euclid
            ratio_e = np.expand_dims(ratio,axis=0)
            rsg = np.squeeze(rp.reshape_grid(ratio_e,trange,1),axis=-1)
            minv,maxv = rsg.min(),rsg.max()
            ax = axes_distance.flat[i]
            ax.set_title("cutoff angle = {}°".format(angle))
            im_distance = ax.imshow(rsg,norm=LogNorm(0.1,10,clip=True),extent=extent)




            delta1 = grid_offset- grid
            delta2 = grid_offset_2 - grid
            angles = anglesBetween(delta1,delta2)


            delta1_projected = grid_offset_projected - grid_projected
            delta2_projected = grid_offset_projected_2 - grid_projected
            angles_projected = anglesBetween(delta1_projected,delta2_projected)
            angle_diff = np.degrees( np.abs(angles-angles_projected))
            angles_formatted = np.squeeze(rp.reshape_grid(angle_diff,trange,1),axis=-1)

            ax = axes_angle.flat[i]
            ax.set_title("cutoff angle = {}°".format(angle))
            im_angle = ax.imshow(angles_formatted,norm=LogNorm(1e-13,30,clip=True),extent=extent)




            area = triangleArea(grid,grid_offset,grid_offset_2)
            area_projected = triangleArea(grid_projected,grid_offset_projected,grid_offset_projected_2)

            area_ratio = np.squeeze(rp.reshape_grid(np.expand_dims(area/area_projected,axis=0),trange,1))

            ax = axes_area.flat[i]
            ax.set_title( "cutoff angle = {}°".format(angle))
            im_area = ax.imshow(area_ratio,norm=LogNorm(0.01,10),extent=extent)



        plt.figure(fig_distance.number)
        cbar = fig_distance.colorbar(im_distance,ax=axes_distance.tolist(),use_gridspec=True)
        cbar.set_label("Ratio of distance on original plane to distance on projected plane")
        fig_distance.suptitle("Distance ratio of transformed line segments with lengths of up to {}".format(limb_length_max))
        plt.savefig('./distance.pdf')

        plt.figure(fig_angle.number)
        cbar = fig_angle.colorbar(im_angle,ax=axes_angle.ravel().tolist(),shrink=0.95)
        cbar.set_label("Angle deviation in °")
        fig_angle.suptitle("Angle difference for limb lengths of up to {}".format(limb_length_max))
        plt.savefig('./angle.pdf')

        plt.figure(fig_area.number)
        cbar = fig_area.colorbar(im_area,ax=axes_area.ravel().tolist())
        cbar.set_label("Area ratio")
        fig_angle.suptitle("Area ratio between right angle triangles with limb lengths up to {}".format(limb_length_max))
        plt.savefig('./area.pdf')