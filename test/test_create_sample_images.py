from unittest import TestCase

import math

from source.complex_log_projection import ComplexLogProjection
from source.hard_coded_providers import get_providers
from source.lat_lng import LatLng
from source.preprojections import IdentityPreprojection
from source.raster_data.function_raster_data_provider import CosSinRasterDataProvider
from source.raster_projector import RasterProjector, TargetSectionDescription
from source.smoothing_functions import DualCosSmoothingFunction
from source.mathutils import euclideanDist
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

        for angle in [0,15,30,45]:
            projection = ComplexLogProjection(LatLng(-1,0),LatLng(1,0),math.radians(angle),smoothing_function_type=DualCosSmoothingFunction,preprojection=IdentityPreprojection())
            trange = TargetSectionDescription(-1.5,1.5,3000,-2,2,4000)
            rp = RasterProjector(projection,CosSinRasterDataProvider)
            grid = rp.build_grid(trange)
            grid_offset = grid+ np.random.uniform(-0.001,0.001,grid.shape)
            euclid = euclideanDist(grid,grid_offset)
            grid_projected = projection(grid)
            grid_offset_projected = projection(grid_offset)
            projected_euclid = euclideanDist(grid_projected,grid_offset_projected)
            ratio = projected_euclid / euclid
            ratio_e = np.expand_dims(ratio,axis=0)
            rsg = np.squeeze(rp.reshape_grid(ratio_e,trange,1),axis=-1)
            minv,maxv = rsg.min(),rsg.max()
            plt.title("Area ratio for cutoff angle "+ str(angle))
            plt.imshow(rsg,norm=LogNorm(0.1,100,clip=True),extent=[trange.xmin,trange.xmax,trange.ymin,trange.ymax])
            plt.colorbar()
            plt.show()
            pass

