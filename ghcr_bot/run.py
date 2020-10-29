#!/usr/bin/env python3
import os
import argparse
import asyncio
import logging

from fan_tools.unix import asucc
from fan_tools.python import py_rel_path


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
log = logging.getLogger('ghcr_bot.run')
BASE_REPO_PATH = os.environ.get('BASE_REPO', 'ghcr.io/ghcr-library/')


def parse_args():
    parser = argparse.ArgumentParser(description='DESCRIPTION')
    parser.add_argument('src', nargs='?', default='./source.txt', type=py_rel_path)
    return parser.parse_args()


async def process():
    pass


def main():
    args = parse_args()
    if not args.src.exists():
        log.warning('No source file found. Exit')
        exit(0)


if __name__ == '__main__':
    main()
