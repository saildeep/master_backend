import logging
import os
import base64
from flask import request

def build_cache_config():
    memcached_url = os.environ.get("MEMCACHED_URL",None)
    general_values = {
        "CACHE_DEFAULT_TIMEOUT": 60*60*24 *7
    }

    if memcached_url is None:
        logging.info("Using simple cache")
        general_values["CACHE_TYPE"] = "simple"
        general_values["CACHE_THRESHOLD"] = 10000
        return general_values
    else:
        logging.info("Using memcached " + memcached_url)
        general_values["CACHE_TYPE"] = "memcached"
        general_values["CACHE_MEMCACHED_SERVERS"] = [memcached_url]
        general_values["CACHE_KEY_PREFIX"] = "be"
        return general_values
def make_url_cache_key(*args,**kwaags):
    k = request.url

    if len(k)>240:
        logging.info("Key to long " + k)
    return k.encode('utf-8')


def make_cache_key(*args, **kwargs):
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    returnable_string = (path + args ).replace(" ","")
    return base64.b64encode(returnable_string.encode('utf-8'))