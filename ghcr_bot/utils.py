import json
import logging
import os
from dataclasses import dataclass
from typing import List

import httpx

from fan_tools.python import py_rel_path


log = logging.getLogger('ghcr_bot.utils')
CACHE_FILE = py_rel_path('../.cache')
if not CACHE_FILE.exists():
    CACHE_FILE.write_text('{}')
CACHE = json.loads(CACHE_FILE.read_text())


GHCR_PATH = 'https://ghcr.io/v2/ghcr-library/'
GHCR_TOKEN = os.environ.get('GHCR_TOKEN')
AUTH_HEADERS = {'Authorization': f'Bearer {GHCR_TOKEN}'}


@dataclass
class ImageInfo:
    name: str
    tags: List[str]


def add_to_cache(path):
    CACHE[path] = True
    CACHE_FILE.write_text(json.dumps(CACHE))


def check_tag(name, tag):
    """
    http HEAD https://ghcr.io/v2/ghcr-library/ubuntu/manifests/focal \
        Authorization:"Bearer ${GHCR_TOKEN}"
    """
    url = f'{GHCR_PATH}{name}/manifests/{tag}'
    if url in CACHE:
        return CACHE[url]
    log.debug(f'Check: {url}')
    resp = httpx.head(url, headers=AUTH_HEADERS, timeout=30)
    if resp.status_code == 200:
        add_to_cache(url)

    return resp.status_code == 200
