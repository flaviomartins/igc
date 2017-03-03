#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
import os
import instagram as ig
from collections import deque

logger = logging.getLogger(__name__)

OUTPUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')


if __name__ == '__main__':
    visited_locations = set()

    visited_users = set()
    user_pq = deque()

    seed_user = 'fctnova'
    # user_pq.inc_priority(seed_user)
    user_pq.append(seed_user)

    while user_pq:
        username = user_pq.popleft()
        visited_users.add(username)
        logger.info("VISITING\t%d\t%s", len(visited_users), username)

        user = ig.get_user(username, OUTPUTDIR, cache='disk')
        if user is not None and 'user' in user:
            u = user['user']
            u_id = u['id']

            if 'media' in u:
                u_media = u['media']
                for i, media in enumerate(u_media['nodes']):
                    ig.download_media(media['display_src'], OUTPUTDIR, media['id'])
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
                                            logger.info("LOCATION\t%s\t%s", loc['id'], loc['name'])

                    if 'comments' in p:
                        p_comments = p['comments']
                        for j, comment in enumerate(p_comments['nodes']):
                            comment_user = comment['user']['username']
                            if comment_user not in visited_users:
                                # user_pq.inc_priority(comment_user)
                                user_pq.append(comment_user)

                    if 'likes' in p:
                        p_likes = p['likes']
                        for j, comment in enumerate(p_likes['nodes']):
                            like_user = comment['user']['username']
                            if like_user not in visited_users:
                                # user_pq.inc_priority(like_user)
                                user_pq.append(like_user)

            # ig_user = ig.get_ig_user(u_id, OUTPUTDIR, cache='disk')
            #
            # if ig_user is not None and 'chaining' in ig_user:
            #     for i, node in enumerate(ig_user['chaining']['nodes']):
            #         chain_user = node['username']
            #         if chain_user not in visited_users:
            #             # user_pq.inc_priority(chain_user)
            #             user_pq.append(chain_user)
