#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import instagram as ig
from maxpq import MaxPq


OUTPUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')


if __name__ == '__main__':
    visited_users = set()
    user_pq = MaxPq()

    seed_user = 'ritacordeiro'
    user_pq.inc_priority(seed_user)

    while user_pq:
        username = user_pq.pop()
        print "Visiting " + str(len(visited_users)) + ": " + username

        visited_users.add(username)
        user = ig.get_user(username, OUTPUTDIR, cache='disk')
        if user is not None and 'user' in user:
            u = user['user']
            u_id = u['id']

            if 'media' in u:
                u_media = u['media']
                for i, node in enumerate(u_media['nodes']):
                    ig.download_media(node['display_src'], OUTPUTDIR, node['id'])
                    media = ig.get_media(node['code'], OUTPUTDIR, cache='disk')

                    if media is not None:
                        p = media['media']

                        if 'location' in p:
                            p_loc = p['location']
                            if p_loc is not None:
                                if 'id' in p_loc:
                                    location = ig.get_location(p_loc['id'], OUTPUTDIR, cache='disk')

            ig_user = ig.get_ig_user(u_id, OUTPUTDIR, cache='disk')

            if ig_user is not None and 'chaining' in ig_user:
                for i, node in enumerate(ig_user['chaining']['nodes']):
                    chain_user = node['username']
                    if chain_user not in visited_users:
                        user_pq.inc_priority(chain_user)
