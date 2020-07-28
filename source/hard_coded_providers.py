from typing import Dict

from source.raster_data.abstract_raster_data_provider import AbstractRasterDataProvider
from source.raster_data.remote_raster_data_provider import RemoteRasterDataProvider
from source.raster_data.tile_resolver import TileURLResolver


def get_providers() -> Dict[str, AbstractRasterDataProvider]:
    _providers: Dict[str, AbstractRasterDataProvider] = {}


    _providers['default'] =  RemoteRasterDataProvider(TileURLResolver(
        url_format="https://a.tile.openstreetmap.de/{2}/{0}/{1}.png"))
    _providers['osm'] = _providers['default']


    _providers['satellite'] =  RemoteRasterDataProvider(TileURLResolver(
        url_format="https://atlas34.inf.uni-konstanz.de/mbtiles/data/openmaptiles_satellite_lowres/{2}/{0}/{1}.jpg"))

    _providers['transparent'] = RemoteRasterDataProvider(TileURLResolver(
        url_format="https://atlas34.inf.uni-konstanz.de/osmtiles/tile/{2}/{0}/{1}.png"))

    for i in [1,2,3,4,5,6]:

        _providers['route' + str(i)] = RemoteRasterDataProvider(TileURLResolver(
            url_format="https://atlas34.inf.uni-konstanz.de/route" +str(i) + "/tile/{2}/{0}/{1}.png"))


    _providers['mapbox'] = RemoteRasterDataProvider(TileURLResolver(
        url_format="https://atlas34.inf.uni-konstanz.de/mapbox/{2}/{0}/{1}.jpg90"))

    return _providers
