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
        x_series = np.linspace(trange.xmin, trange.xmax, num=trange.xsteps)
        y_series = np.linspace(trange.ymin, trange.ymax, num=trange.ysteps)

        xy = np.zeros((2, trange.xsteps * trange.ysteps))
        i = 0
        for y in y_series:
            for x in x_series:
                xy[0, i] = x
                xy[1, i] = y
                i += 1

        return xy

    def reshape_grid(self, data: np.ndarray, trange: TargetSectionDescription, channels):
        assert data.shape == (channels, trange.xsteps * trange.ysteps)
        data_reshaped = np.reshape(np.transpose(data), (trange.ysteps, trange.xsteps, channels))
        return data_reshaped

    # (y,x,3) array with corresping (lat,lng,zoom) information
    def project(self, trange: TargetSectionDescription) -> np.ndarray:
        grid = self.build_grid(trange)
        inverted = self.projection.invert(grid)
        zoom = np.expand_dims(self.projection.getZoomLevel(grid), axis=0)
        position_and_zoom = np.concatenate([inverted, zoom], axis=0)
        data = self.data_source.getData(position_and_zoom)
        data_reshaped = self.reshape_grid(data, trange, 3)
        return data_reshaped
