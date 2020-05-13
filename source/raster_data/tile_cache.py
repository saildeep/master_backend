import abc
import os
import tempfile
import warnings
from threading import RLock, current_thread
from typing import Optional, List

from PIL import Image
from contextlib import suppress

from source.raster_data.tile_math import OSMTile
from source.raster_data.tile_resolver import AbstractTileImageResolver

from collections import OrderedDict

from logging import debug


class TileFilenameResolver:
    def __init__(self):
        self.basedir = os.path.join(tempfile.gettempdir(), "osmtiles")
        if os.path.isfile(self.basedir):
            raise EnvironmentError("File with name of basedir exists")

        if not os.path.isdir(self.basedir):
            os.mkdir(self.basedir)

    def __call__(self, tile: OSMTile) -> str:
        return os.path.join(self.basedir, "{0}-{1}-{2}.png".format(tile.x, tile.y, tile.zoom))


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


class FileTileCache(AbstractTileImageResolver):

    def __init__(self, fallback: AbstractTileImageResolver,
                 filename_resolver: TileFilenameResolver = TileFilenameResolver()):

        self.fallback = fallback
        self.filename_resolver = filename_resolver
        self.locks = []
        for i in range(8192):
            self.locks.append(RLock())

    def __call__(self, tile: OSMTile) -> Image:
        mylock = self.locks[tile.__hash__() % len(self.locks)]
        with mylock:
            im = self.getCache(tile)
            if im is not None:
                return im
            im = self.fallback(tile)
            assert im is not None
            self.putCache(tile, im)
            return im

    def getCache(self, tile: OSMTile) -> Optional[Image.Image]:

        path = self.filename_resolver(tile)
        if os.path.isfile(path):
            debug(str(current_thread()) + " reading " + path)
            im: Image.Image = Image.open(path, mode='r')
            return im.copy()
        else:
            return None

    def putCache(self, tile: OSMTile, image: Image.Image):

        path = self.filename_resolver(tile)
        # TODO make writing atomic
        if not os.path.isfile(path):
            image.save(path, "PNG")
        else:
            warnings.warn("Tried to write " + path + " to cached but it already existed")


class MemoryTileCache(AbstractTileImageResolver):

    def __init__(self, fallback: AbstractTileImageResolver, mem_size=500000, lock=False):

        self.fallback = fallback
        self.storage = OrderedDict()
        self.mem_size = mem_size
        self.existant_storage = {}

        self.locks = []
        for i in range(8192):
            if lock:
                self.locks.append(RLock())
            else:
                self.locks.append(suppress())

    def __call__(self, tile: OSMTile) -> Image:

        mylock = self.locks[tile.__hash__() % len(self.locks)]

        with mylock:
            # assume this is atomic
            im = self.storage.get(tile.__hash__(), None)
            if im is not None:
                return im
            else:
                may_exist = self.existant_storage.get(tile.__hash__(), True)
                if may_exist:
                    try:
                        im = self.fallback(tile)
                    except FileNotFoundError:
                        self.existant_storage[tile.__hash__()] = False
                        print("Marked " + tile.__str__() + "as non existant")
                        raise FileNotFoundError()

                    assert im is not None
                    self.storage[tile.__hash__()] = im
                    while len(self.storage) > self.mem_size:
                        self.storage.popitem(last=False)
                    return im
                else:
                    raise FileNotFoundError()
