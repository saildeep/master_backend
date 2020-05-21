from source.raster_data.tile_cache import TileFilenameResolver, MemoryTileCache, FileTileCache
from source.raster_data.tile_resolver import HTTPTileFileResolver, TileURLResolver



def get_dummy_resolver():
    r = HTTPTileFileResolver(TileURLResolver(
        url_format="https://a.tile.openstreetmap.de/{2}/{0}/{1}.png"))
    r = FileTileCache(r, TileFilenameResolver("osm_test"))
    r = MemoryTileCache(r, mem_size=100000)
    return r

dummy_resolver = get_dummy_resolver()