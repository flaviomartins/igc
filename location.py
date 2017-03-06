#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import io
import logging
import fnmatch
import os
import sys
try:
    import ujson as json
except ImportError:
    import json
import fiona

from shapely.geometry import Point, asShape

logger = logging.getLogger(__name__)

DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


shapes = {}
locations = []


def whereisthis(lng, lat):
    point = Point(lng, lat)  # longitude, latitude
    for k, v in shapes.items():
        if point.within(v):
            return k
            break
    return None


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: location.py <basedir>")
        sys.exit(0)

    with fiona.open(os.path.join(DATADIR, "PRT_adm_shp/PRT_adm1.shp")) as fiona_collection:
        for shapefile_record in fiona_collection:
            name = shapefile_record['properties']['NAME_1'] + ", " + shapefile_record['properties']['NAME_0']
            shapes[name] = asShape(shapefile_record['geometry'])
            shapes[name] = shapes[name].simplify(10e-6, preserve_topology=False)

    matches = []
    for root, dirnames, filenames in os.walk(sys.argv[1]):
        for filename in fnmatch.filter(filenames, '*.json'):
            matches.append(os.path.join(root, filename))

    for m in matches:
        with io.open(m, 'rt', encoding='utf-8') as f:
            location = json.load(f)

        if location is not None and 'location' in location:
            loc = location['location']
            if loc['lng'] is not None and loc['lat'] is not None:
                locations.append({'id': loc['id'], 'name': loc['name'], 'lng': loc['lng'], 'lat': loc['lat']})
                place = whereisthis(loc['lng'], loc['lat'])
                if place is not None:
                    logger.info("%s\t%s", place, loc['name'])

    with io.open(os.path.join(DATADIR, "locations.json"), 'w', encoding='utf-8') as f:
        json.dump(locations, f, sort_keys=True, indent=4)
