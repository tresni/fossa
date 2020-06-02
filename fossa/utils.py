import os

from fossa import APP_NAME

import click
import requests
import requests_cache


def Session(name, *args, **kwargs):
    return requests.Session()


def CachedSession(name, cache=300, *args, **kwargs):
    name = ''.join(list(filter(lambda k: str.isalpha(k) or str.isdigit(k) or k == '-', list(name))))
    path = os.path.join(click.get_app_dir(APP_NAME), name)
    return requests_cache.CachedSession(path, expire_after=cache, include_get_headers=True)
