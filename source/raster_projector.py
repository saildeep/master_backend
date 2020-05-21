from source.raster_data.abstract_raster_data_provider import AbstractRasterDataProvider

import numpy as np

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
    def project(self, trange: TargetSectionDescription) -> np.ndarray:
        grid = self.build_grid(trange)
        inverted = self.projection.invert(grid)
        pixel_per_unit = trange.xsteps / (trange.xmax - trange.xmin)
        zoom = np.expand_dims(self.projection.getZoomLevel(grid, pixel_per_unit), axis=0)
        position_and_zoom = np.concatenate([inverted, zoom], axis=0)
        data = self.data_source.getData(position_and_zoom)
        data_reshaped = self.reshape_grid(data, trange, 3)
        return data_reshaped
