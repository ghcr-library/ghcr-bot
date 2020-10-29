#!/usr/bin/env python3
import time
import argparse
import logging
import os
import json
from pathlib import Path
from typing import List

import httpx

from fan_tools.python import py_rel_path
from fan_tools.unix import succ

from ghcr_bot.utils import ImageInfo


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
log = logging.getLogger('ghcr_bot.gen_sources')
SRC_REPO = 'https://github.com/docker-library/official-images.git'
IMAGES_REPO = py_rel_path('../../official-images')
LIB = IMAGES_REPO / 'library'
GHCR_TOKEN = os.environ.get('GHCR_TOKEN')
AUTH_HEADERS = {'Authorization': f'Bearer {GHCR_TOKEN}'}
GHCR_PATH = 'https://ghcr.io/v2/ghcr-library/'
CACHE_FILE = py_rel_path('../.cache')
if not CACHE_FILE.exists():
    CACHE_FILE.write_text('{}')
CACHE = json.loads(CACHE_FILE.read_text())
STOP_WORDS = ['windowsservercore']


def add_to_cache(path):
    CACHE[path] = True
    CACHE_FILE.write_text(json.dumps(CACHE))


def parse_args():
    parser = argparse.ArgumentParser(description='DESCRIPTION')
    parser.add_argument('images', nargs='+')
    parser.add_argument('--all-absent', action='store_true')
    parser.add_argument('--out', default='./source.txt', type=Path)
    parser.add_argument('--split', action='store_true')
    parser.add_argument('--no-sync', action='store_true')
    return parser.parse_args()


def sync_repo(args):
    if not IMAGES_REPO.exists():
        log.info(f'Clone repo: {SRC_REPO}')
        succ(f'cd {IMAGES_REPO.parent} && git clone {SRC_REPO}')
        return
    if args.no_sync:
        return

    log.info('Pull changes')
    succ(f'cd {IMAGES_REPO} && git pull -r')


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


def parse_image(args, name: str) -> ImageInfo:
    fname = LIB / name
    if not fname.exists():
        log.error(f'Cannot find file: {fname}')
        exit(1)
    tags = []
    for line in fname.read_text().split('\n'):
        if line.startswith('Tags: '):
            tags.extend(line.replace('Tags: ', '').split(', '))
    return ImageInfo(name=name, tags=tags)


def gen_missing_info(args, info: ImageInfo) -> ImageInfo:
    missing_tags = []
    for tag in info.tags:
        if not args.all_absent and  check_tag(info.name, tag):
            continue
        for stop_word in STOP_WORDS:
            if stop_word in tag:
                continue
        missing_tags.append(tag)
    log.info(f'Missing info: {info.name}:{missing_tags}')
    return ImageInfo(name=info.name, tags=missing_tags)


def info_to_line(source: ImageInfo) -> str:
    return f'{source.name} {" ".join(source.tags)}\n'


def write_splitted(args, sources: List[ImageInfo]):
    fname: Path = args.out
    for source in sources:
        if source.tags:
            fname.write_text(info_to_line(source))
            succ(f'git add {fname}')
            succ(f'git commit -m "remove me: {source.name}"')
            succ(f'git push')
            time.sleep(10)


def write_source(args, sources: List[ImageInfo]):
    fname: Path = args.out
    with fname.open('w') as f:
        for source in sources:
            if source.tags:
                f.write(info_to_line(source))


def main():
    args = parse_args()
    sync_repo(args)
    sources = []
    for name in args.images:
        log.info(f'Check container: {name}')
        info = parse_image(args, name)
        sources.append(gen_missing_info(args, info))
    if args.split:
        write_splitted(args, sources)
    else:
        write_source(args, sources)


if __name__ == '__main__':
    main()
