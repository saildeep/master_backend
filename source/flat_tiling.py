"""
Used for mapping the projection to a tiled space and back
"""


class FlatTiling():
    def __init__(self, top_level_range):
        self.top_level_range = top_level_range

        self.start_x = -top_level_range
        self.start_y = -top_level_range

    def __call__(self, x: int, y: int, zoom: int):
        zoom_size = 2 ** zoom

        tile_width = self.top_level_range * 2 / zoom_size

        xmin = x * tile_width + self.start_x
        ymin = y * tile_width + self.start_y
        xmax = xmin + tile_width
        ymax = ymin + tile_width

        return (xmin, ymin, xmax, ymax)
