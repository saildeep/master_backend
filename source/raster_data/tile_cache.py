import abc
import os
import tempfile
import warnings
from threading import Lock
from typing import Optional, List
import io
from PIL import Image

from source.raster_data.tile_math import OSMTile
from source.raster_data.tile_resolver import AbstractTileImageResolver


class TileFilenameResolver:
    def __init__(self):
        self.basedir = os.path.join(tempfile.gettempdir(), "osmtiles")
        if os.path.isfile(self.basedir):
            raise EnvironmentError("File with name of basedir exists")

        if not os.path.isdir(self.basedir):
            os.mkdir(self.basedir)

    def __call__(self, tile: OSMTile) -> str:
        return os.path.join(self.basedir, "{2}-{0}-{1}.png".format(tile.x, tile.y, tile.zoom))


class AbstractCacheRule(abc.ABC):
    @abc.abstractmethod
    def __call__(self, tile: OSMTile) -> bool:
        pass

    def removable(self) -> List[OSMTile]:
        return []

    def remove(self, tile: OSMTile):
        pass

    def put(self, tile: OSMTile):
        pass


class MaxZoomLevelCacheRule(AbstractCacheRule):

    def __init__(self, max_zoom_level: int):
        self.max_zoom_level = max_zoom_level

    def __call__(self, tile: OSMTile) -> OSMTile:
        return tile.zoom <= self.max_zoom_level


class LastUsedCacheRule(AbstractCacheRule):
    def __init__(self, max_elements: int):
        self.max_elements = max_elements
        self.counter = 0
        self.storage = []

    def __call__(self, tile: OSMTile) -> bool:
        return True

    def put(self, tile: OSMTile):
        self.storage.append(tile.__str__())

    def remove(self, tile: OSMTile):
        # should be fast as remvoable elements are always at the start of the list
        del self.storage[self.storage.index(tile.__str__())]

    def removable(self) -> List[OSMTile]:
        to_index = max(len(self.storage) - self.max_elements, 0)
        return self.storage[0:to_index]


# According to rules put things in the cache
class AbstractTileCache(AbstractTileImageResolver):
    def __init__(self, fallback: AbstractTileImageResolver, rules: List[AbstractCacheRule]):
        self.fallback = fallback
        self.rules = rules

        num_locks = 128
        self.locks = []
        for l in range(num_locks):
            self.locks.append(Lock())

    def __call__(self, tile: OSMTile) -> Image.Image:
        lock = self.locks[tile.__hash__()%len(self.locks)]
        with lock:
            res = self.getCache(tile)

            if res is not None:
                return res

            res = self.fallback(tile)
            if res is None:
                raise FileNotFoundError("Could not resolver " + tile.__str__())
            for rule in self.rules:
                if rule(tile):
                    rule.put(tile)
                    self.putCache(tile, res)
                    # clean up cache after inserting the new one
                    for removeable_tile in rule.removable():
                        rule.remove(removeable_tile)
                        self.removeCache(removeable_tile)

                    break
            return res

    @abc.abstractmethod
    def getCache(self, tile: OSMTile) -> Optional[Image.Image]:
        pass

    @abc.abstractmethod
    def putCache(self, tile: OSMTile, image: Image.Image):
        pass

    @abc.abstractmethod
    def removeCache(self, tile: OSMTile):
        pass


class FileTileCache(AbstractTileCache):

    def __init__(self, fallback: AbstractTileImageResolver, rules: List[AbstractCacheRule],
                 filename_resolver: TileFilenameResolver = TileFilenameResolver()):
        super(FileTileCache, self).__init__(fallback, rules)
        self.filename_resolver = filename_resolver

    def getCache(self, tile: OSMTile) -> Optional[Image.Image]:
        path = self.filename_resolver(tile)
        if os.path.isfile(path):
            im = 1
            with open(path, "rb") as f:
                im = Image.open(io.BytesIO(f.read()))
            return im
        else:
            return None

    def putCache(self, tile: OSMTile, image: Image.Image):
        path = self.filename_resolver(tile)
        if not os.path.isfile(path):
            image.save(path, "PNG")
        else:
            warnings.warn("Tried to write " + path + " to cached but it already existed")

    def removeCache(self, tile: OSMTile):
        path = self.filename_resolver(tile)
        os.remove(path)


class MemoryTileCache(AbstractTileCache):

    def __init__(self, fallback: AbstractTileImageResolver, rules: List[AbstractCacheRule]):
        super(MemoryTileCache, self).__init__(fallback, rules)
        self.storage = {}

    def getCache(self, tile: OSMTile) -> Optional[Image.Image]:
        hash = tile.__str__()
        if hash in self.storage:
            return self.storage[hash]
        return None

    def putCache(self, tile: OSMTile, image: Image.Image):
        self.storage[tile.__str__()] = image

    def removeCache(self, tile: OSMTile):
        del self.storage[tile]
