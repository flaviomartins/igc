#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from builtins import object

import fnmatch
import os
import sys
import json
import instagram as ig
import concurrent.futures


class FoundFilenames(object):
    def __init__(self, basedir):
        self.basedir = basedir

    def __iter__(self):
        for root, dirnames, filenames in os.walk(self.basedir):
            for filename in fnmatch.filter(filenames, '*.json'):
                with open(os.path.join(root, filename)) as f:
                    yield json.load(f)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: threaded_download_media.py <basedir> <outputdir>")
        sys.exit(0)

    basedir = sys.argv[1]
    outputdir = sys.argv[2]

    for p in FoundFilenames(basedir):
        if p is not None and 'media' in p:
            media = p['media']

            if 'id' in media and 'display_src' in media:
                # ig.download_media(media['display_src'], sys.argv[2], media['id'])
                print(media['display_src'])
