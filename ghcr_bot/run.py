#!/usr/bin/env python3
import argparse
import asyncio
import logging
import os
from pathlib import Path

from fan_tools.unix import asucc

from ghcr_bot.utils import ImageInfo


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
log = logging.getLogger('ghcr_bot.run')
BASE_REPO_PATH = os.environ.get('BASE_REPO', 'ghcr.io/ghcr-library/')


def parse_args():
    parser = argparse.ArgumentParser(description='DESCRIPTION')
    parser.add_argument('src', nargs='?', default='./source.txt', type=Path)
    return parser.parse_args()


def parse_image_info(line: str) -> ImageInfo:
    name, *tags = line.split(' ')
    return ImageInfo(name=name, tags=tags)


async def sync_image(image: str, tag: str):
    log.info(f'Run sync for {image}:{tag}')
    old = f'{image}:{tag}'
    new = f'{BASE_REPO_PATH}{image}:{tag}'

    for cmd in [f'docker pull {old}', f'docker tag {old} {new}', f'docker push {new}']:
        log.debug(f'CMD: {cmd}')
        await asucc(cmd)


async def sync_tags(image: ImageInfo):
    for tag in image.tags:
        await sync_image(image.name, tag)


async def process(args):
    src: Path = args.src
    for line in src.read_text().split('\n'):
        if not line:
            continue
        await sync_tags(parse_image_info(line))


def main():
    args = parse_args()
    if not args.src.exists():
        log.warning('No source file found. Exit')
        exit(0)

    loop = asyncio.get_event_loop()
    main_task = loop.create_task(process(args))
    loop.run_until_complete(main_task)


if __name__ == '__main__':
    main()
