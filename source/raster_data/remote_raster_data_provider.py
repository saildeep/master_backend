from typing import Optional

from source.raster_data.abstract_raster_data_provider import AbstractRasterDataProvider
from source.raster_data.tile_math import latlngZoomToXYZoomNP

import base64
import numpy as np
import requests

from source.raster_data.tile_resolver import TileURLResolver


class RemoteRasterDataProvider(AbstractRasterDataProvider):

    def __init__(self, urlresovler: TileURLResolver):
        self.resolver = urlresovler
        super(RemoteRasterDataProvider, self).__init__()

    def getSampleFN(self):
        return sample

    def get_init_params(self, manager: Optional[object]):
        return self.resolver,

    def init_process(self, resolver):
        b64_suburl = base64.b64encode(resolver.normalized().encode('utf-8')).decode('utf-8')
        return {
            "resolver_url": "http://localhost:8000/resolve/"+b64_suburl,

        }


def sample(latlng: np.ndarray, init_data):
    xyzoom = latlngZoomToXYZoomNP(latlng)
    xyzoom_clipped = xyzoom.astype(np.uint32)

    binary = xyzoom_clipped.tobytes()
    resp = requests.post(init_data['resolver_url'], data=binary, headers={'Content-Type': 'application/octet-stream'})
    res_con = resp.content
    pass