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

    def _build_grid(self, trange: TargetSectionDescription):
        x_series = np.linspace(trange.xmin, trange.xmax, num=trange.xsteps)
        y_series = np.linspace(trange.ymin, trange.ymax, num=trange.ysteps)

        xy = np.zeros((2, trange.xsteps * trange.ysteps))
        i = 0
        for x in x_series:
            for y in y_series:
                xy[0, i] = x
                xy[1, i] = y
                i += 1

        return xy

    def project(self, range: TargetSectionDescription) -> np.ndarray:
        grid = self._build_grid(range)
        inverted = self.projection.invert(grid)
        zoom = np.expand_dims(self.projection.getZoomLevel(grid), axis=0)
        position_and_zoom = np.concatenate([inverted, zoom], axis=0)
        data = self.data_source.getData(position_and_zoom)
        data_reshaped = np.reshape(np.transpose(data), (range.ysteps, range.xsteps, 3))
        return data_reshaped
