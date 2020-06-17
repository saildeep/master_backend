from logging import info
from typing import Optional

from source.raster_data.abstract_raster_data_provider import AbstractRasterDataProvider
from source.raster_data.tile_math import latlngZoomToXYZoomNP

import base64
import numpy as np
import requests
import os

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
        server = os.environ.get("TILERESOLVER","127.0.0.1:8000")
        return {
            "resolver_url": "http://"+server+"/resolve/"+b64_suburl + "/resolution/256",

        }


def sample(latlng: np.ndarray, init_data):
    num_elements = latlng.shape[1]
    xyzoom = latlngZoomToXYZoomNP(latlng)
    xy = (xyzoom[0:2,:] * 256).astype(np.uint32)
    zoom = (xyzoom[2:,:]*256).astype(np.uint32)
    xyzoom_clipped = np.concatenate([xy,zoom],axis=0)
    assert xyzoom_clipped.shape == xyzoom.shape
    xyzoom_clipped =xyzoom_clipped.transpose()

    binary = xyzoom_clipped.tobytes()
    resp = requests.post(init_data['resolver_url'], data=binary, headers={'Content-Type': 'application/octet-stream'})
    if(resp.status_code != 200):
        info("Received status {0}".format(resp.status_code) )
    res_con = resp.content
    parsed_resp = np.frombuffer(res_con,np.uint8).reshape(num_elements,4).transpose()
    assert parsed_resp.shape == (4,xyzoom.shape[1])
    return parsed_resp