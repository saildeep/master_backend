from source.raster_data.abstract_raster_data_provider import AbstractRasterDataProvider

import numpy as np
import math
from source.zoomable_projection import ZoomableProjection


class TargetSectionDescription():
    def __init__(self, xmin: float, xmax: float, xsteps: int, ymin: float, ymax: float, ysteps: int):
        self.xmin = xmin
        self.xmax = xmax
        self.xsteps = xsteps
        self.ymin = ymin
        self.ymax = ymax
        self.ysteps = ysteps


class RasterProjector():
    def __init__(self, projection: ZoomableProjection, data_source: AbstractRasterDataProvider):
        self.projection = projection
        self.data_source = data_source

    def build_grid(self, trange: TargetSectionDescription) -> np.ndarray:
        x_series = np.expand_dims(np.linspace(trange.xmin, trange.xmax, num=trange.xsteps), axis=0)
        y_series = np.expand_dims(np.linspace(trange.ymin, trange.ymax, num=trange.ysteps), axis=1)
        y_extended = (y_series * np.ones_like(x_series)).flatten()
        x_extended = (x_series * np.ones_like(y_series)).flatten()
        stacked = np.stack([x_extended, y_extended], axis=0)
        return stacked

    def reshape_grid(self, data: np.ndarray, trange: TargetSectionDescription, channels):
        assert data.shape == (channels, trange.xsteps * trange.ysteps)
        data_reshaped = np.reshape(np.transpose(data), (trange.ysteps, trange.xsteps, channels))
        return data_reshaped

    # (y,x,3) array with corresping (lat,lng,zoom) information
    def project(self, trange: TargetSectionDescription,clip_color =[0,0,0,0]) -> np.ndarray:

        use_clipping = True
        if clip_color is not None:
            clip_color = np.asarray(clip_color).astype(np.uint8)
            assert clip_color.shape == (4,)
            assert clip_color.dtype == np.uint8
        else:
            use_clipping = False
            clip_color = np.array([0,0,0,0],dtype=np.uint8)

        grid = self.build_grid(trange)
        clip_map = np.logical_and(use_clipping,  np.logical_or(grid[1,:] > math.pi,grid[1,:] < -math.pi))
        project_map = np.invert(clip_map)
        to_project_grid = grid[:,project_map]
        inverted = self.projection.invert(to_project_grid)
        pixel_per_unit = trange.xsteps / (trange.xmax - trange.xmin)
        zoom = np.expand_dims(self.projection.getZoomLevel(to_project_grid, pixel_per_unit), axis=0)
        position_and_zoom = np.concatenate([inverted, zoom], axis=0)
        data = self.data_source.getData(position_and_zoom)
        flat = np.repeat(np.expand_dims(clip_color,1),grid.shape[1],1)
        flat[:,project_map] = data

        data_reshaped = self.reshape_grid(flat, trange, data.shape[0])
        return data_reshaped
