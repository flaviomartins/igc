#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from builtins import str
from builtins import range

import fnmatch
import os
import sys
try:
    import ujson as json
except ImportError:
    import json
import fiona
import instagram as ig
from maxpq import MaxPq
from collections import deque
from pprint import pprint

from shapely.geometry import Point, asShape


DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
OUTPUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')


shapes = {}

user_pq = MaxPq()
visited_users = set()

location_pq = deque()
visited_locations = set()


def whereisthis(lng, lat):
    point = Point(lng, lat)  # longitude, latitude
    for k, v in shapes.items():
        if point.within(v):
            return k
            break
    return None


if __name__ == '__main__':
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
        with open(m, 'r') as f:
            location = json.load(f)

        if location is not None and 'location' in location:
            loc = location['location']
            if loc['lng'] is not None and loc['lat'] is not None:
                place = whereisthis(loc['lng'], loc['lat'])
                if place is not None:
                    location_pq.append(loc['id'])

    while location_pq:
        loc_id = location_pq.pop()
        print("VISITING", "\t", str(len(visited_locations)), "\t", loc_id)
        location = ig.get_location(loc_id, OUTPUTDIR, cache='disk')
        if location is not None and 'location' in location:
            loc = location['location']
            print(place.encode('utf-8'), "\t", loc['name'].encode('utf-8'))

            if loc['id'] not in visited_locations:
                visited_locations.add(loc['id'])
                if 'top_posts' in loc:
                    loc_top_posts = loc['top_posts']
                    for i, media in enumerate(loc_top_posts['nodes']):
                        # ig.download_media(media['display_src'], OUTPUTDIR, media['id'])
                        pmedia = ig.get_media(media['code'], OUTPUTDIR, cache='disk')

                        if pmedia is not None:
                            p = pmedia['media']

                            if 'owner' in p:
                                username = p['owner']['username']
                                user_pq.inc_priority(username)

                if 'media' in loc:
                    loc_media = loc['media']
                    for i, media in enumerate(loc_media['nodes']):
                        # ig.download_media(media['display_src'], OUTPUTDIR, media['id'])
                        pmedia = ig.get_media(media['code'], OUTPUTDIR, cache='disk')

                        if pmedia is not None:
                            p = pmedia['media']

                            if 'owner' in p:
                                username = p['owner']['username']
                                user_pq.inc_priority(username)

                i = 0
                top_users = []
                for i in range(len(user_pq.pq)):
                    if len(top_users) > 9:
                        break
                    username = user_pq.pq[i][2]
                    if username not in top_users:
                        top_users.append(username)
                    i += 1
                pprint(top_users)

    while user_pq:
        username = user_pq.pop()
        visited_users.add(username)
        print("VISITING", "\t", str(len(visited_users)), "\t", username)

        user = ig.get_user(username, OUTPUTDIR, cache='disk')
        if user is not None and 'user' in user:
            u = user['user']
            u_id = u['id']

            if 'media' in u:
                u_media = u['media']
                for i, media in enumerate(u_media['nodes']):
                    # ig.download_media(media['display_src'], OUTPUTDIR, media['id'])
                    pmedia = ig.get_media(media['code'], OUTPUTDIR, cache='disk')

                    if pmedia is not None:
                        p = pmedia['media']

                        if 'location' in p:
                            p_loc = p['location']
                            if p_loc is not None:
                                if 'id' in p_loc:
                                    location = ig.get_location(p_loc['id'], OUTPUTDIR, cache='disk')
                                    if location is not None and 'location' in location:
                                        loc = location['location']
                                        if loc['id'] not in visited_locations:
                                            visited_locations.add(loc['id'])
                                            print("LOCATION", "\t", loc['id'], "\t", loc['name'])

                    # if 'comments' in p:
                    #     p_comments = p['comments']
                    #     for j, comment in enumerate(p_comments['nodes']):
                    #         comment_user = comment['user']['username']
                    #         if comment_user not in visited_users:
                    #             # user_pq.inc_priority(comment_user)
                    #             user_pq.append(comment_user)
                    #
                    # if 'likes' in p:
                    #     p_likes = p['likes']
                    #     for j, comment in enumerate(p_likes['nodes']):
                    #         like_user = comment['user']['username']
                    #         if like_user not in visited_users:
                    #             # user_pq.inc_priority(like_user)
                    #             user_pq.append(like_user)
                    #
                    # ig_user = ig.get_ig_user(u_id, OUTPUTDIR, cache='disk')
                    #
                    # if ig_user is not None and 'chaining' in ig_user:
                    #     for i, node in enumerate(ig_user['chaining']['nodes']):
                    #         chain_user = node['username']
                    #         if chain_user not in visited_users:
                    #             # user_pq.inc_priority(chain_user)
                    #             user_pq.append(chain_user)
