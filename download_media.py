#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fnmatch
import os
import sys
import json
import instagram as ig


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: download_media.py <basedir> <outputdir>"
        sys.exit(0)

    matches = []
    for root, dirnames, filenames in os.walk(sys.argv[1]):
        for filename in fnmatch.filter(filenames, '*.json'):
            with open(os.path.join(root, filename), 'r') as f:
                p = json.load(f)

            if p is not None and 'media' in p:
                media = p['media']

                if 'id' in media and 'display_src' in media:
                    ig.download_media(media['display_src'], sys.argv[2], media['id'])
