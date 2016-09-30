import fnmatch
import os
import json
import fiona

from shapely.geometry import Point, asShape


DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


shapes = {}


def whereisthis(lng, lat):
    point = Point(lng, lat)  # longitude, latitude
    for k, v in shapes.iteritems():
        if point.within(v):
            return k
            break
    return None


with fiona.open(os.path.join(DATADIR, "PRT_adm_shp/PRT_adm1.shp")) as fiona_collection:
    for shapefile_record in fiona_collection:
        name = shapefile_record['properties']['NAME_1'] + ", " + shapefile_record['properties']['NAME_0']
        shapes[name] = asShape(shapefile_record['geometry'])
        shapes[name] = shapes[name].simplify(10e-6, preserve_topology=False)

matches = []
for root, dirnames, filenames in os.walk('out/explore/locations/'):
    for filename in fnmatch.filter(filenames, '*.json'):
        matches.append(os.path.join(root, filename))

for m in matches:
    with open(m, 'r') as f:
        data = json.load(f)

    loc = data['location']
    if loc['lng'] is not None and loc['lat'] is not None:
        place = whereisthis(loc['lng'], loc['lat'])
        if place is not None:
            print m, "\t", place.encode('utf-8'), "\t", loc['name'].encode('utf-8')
