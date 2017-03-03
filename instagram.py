#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from builtins import str

import logging
import os
import time
try:
    import ujson as json
except ImportError:
    import json
import requests
from requests.exceptions import ConnectionError, ReadTimeout
from requests.packages.urllib3.exceptions import ReadTimeoutError
import shutil

logger = logging.getLogger(__name__)

PROTOCOL = 'https'
BASE_URL = 'www.instagram.com'
SESSION_PARAMS = {'__a': '1'}

DELAY = 0.1


USER_PATH = 'user'
MEDIA_PATH = 'p'
MEDIA_DOWNLOAD_PATH = 'media'
LOCATION_PATH = 'explore/locations'
TAGS_PATH = 'explore/tags'

IG_USER_PATH = 'ig_user'

QUERY_URL = PROTOCOL + '://' + '/'.join([BASE_URL, 'query']) + '/'


def get_user_url(username):
    return PROTOCOL + '://' + '/'.join([BASE_URL, username]) + '/'


def get_media_url(code):
    return PROTOCOL + '://' + '/'.join([BASE_URL, MEDIA_PATH, code]) + '/'


def get_tag_url(tag):
    return PROTOCOL + '://' + '/'.join([BASE_URL, TAGS_PATH, tag]) + '/'


def get_location_url(location_id):
    return PROTOCOL + '://' + '/'.join([BASE_URL, LOCATION_PATH, location_id]) + '/'


def get_user(username, basedir, cache=None):
    user = None
    path = os.path.join(basedir, os.path.join(USER_PATH, username[:1]))
    fullpath = os.path.join(path, username) + '.json'

    cached = False
    if cache == 'disk':
        if os.path.exists(fullpath):
            with open(fullpath, 'rb') as f:
                user = json.load(f)
                cached = True

    if not cached:
        time.sleep(DELAY)
        session = requests.Session()
        session.params = SESSION_PARAMS
        url = get_user_url(username)

        try:
            r = session.get(url, timeout=5)
            if r.status_code == 200:
                if cache == 'disk':
                    try:
                        os.makedirs(path)
                    except OSError:
                        pass

                    with open(fullpath, 'wb') as f:
                        f.write(r.content)

                user = r.json()
                logger.info("user %s fetched.", username)
        except ConnectionError:
            pass
        except ReadTimeout:
            pass

    return user


def get_media(code, basedir, cache=None):
    media = None
    path = os.path.join(basedir, os.path.join(MEDIA_PATH, code[:3]))
    fullpath = os.path.join(path, code) + '.json'

    cached = False
    if cache == 'disk':
        if os.path.exists(fullpath):
            with open(fullpath, 'rb') as f:
                media = json.load(f)
                cached = True

    if not cached:
        time.sleep(DELAY)
        session = requests.Session()
        session.params = SESSION_PARAMS
        url = get_media_url(code)

        try:
            r = session.get(url, timeout=5)
            if r.status_code == 200:
                if cache == 'disk':
                    try:
                        os.makedirs(path)
                    except OSError:
                        pass

                    with open(fullpath, 'wb') as f:
                        f.write(r.content)

                media = r.json()
                logger.info("media p %s fetched.", code)
        except ConnectionError:
            pass
        except ReadTimeout:
            pass

    return media


def get_location(location_id, basedir, cache=None):
    location = None
    path = os.path.join(basedir, os.path.join(LOCATION_PATH, location_id[:3]))
    fullpath = os.path.join(path, location_id) + '.json'

    cached = False
    if cache == 'disk':
        if os.path.exists(fullpath):
            with open(fullpath, 'rb') as f:
                location = json.load(f)
                cached = True

    if not cached:
        time.sleep(DELAY)
        session = requests.Session()
        session.params = SESSION_PARAMS
        url = get_location_url(location_id)

        try:
            r = session.get(url, timeout=5)
            if r.status_code == 200:
                if cache == 'disk':
                    try:
                        os.makedirs(path)
                    except OSError:
                        pass

                    with open(fullpath, 'wb') as f:
                        f.write(r.content)

                location = r.json()
                # print "location " + location_id + " fetched."
        except ConnectionError:
            pass
        except ReadTimeout:
            pass

    return location


def get_ig_user(user_id, basedir, cache=None):
    q = 'ig_user(' + str(user_id) + ''') {
      chaining {
        nodes {
          blocked_by_viewer,
          followed_by_viewer,
          followed_by_viewer,
          follows_viewer,
          full_name,
          has_blocked_viewer,
          has_requested_viewer,
          id,
          is_private,
          is_verified,
          profile_pic_url,
          requested_by_viewer,
          username
        }
      }
    }'''

    ig_user = None
    path = os.path.join(basedir, os.path.join(IG_USER_PATH, user_id[:3]))
    fullpath = os.path.join(path, str(user_id)) + '.json'

    cached = False
    if cache == 'disk':
        if os.path.exists(fullpath):
            with open(fullpath, 'rb') as f:
                ig_user = json.load(f)
                cached = True

    if not cached:
        time.sleep(DELAY)
        session = requests.Session()
        params = {'q': q}

        try:
            r = session.get(QUERY_URL, params=params, timeout=5)
            if r.status_code == 200:
                if cache == 'disk':
                    try:
                        os.makedirs(path)
                    except OSError:
                        pass

                    with open(fullpath, 'wb') as f:
                        f.write(r.content)

                ig_user = r.json()
                # print "ig_user " + str(user_id) + " fetched."
        except ConnectionError:
            pass
        except ReadTimeout:
            pass

    return ig_user


def download_media(url, basedir, name):
    filename = name + '.jpg'
    path = os.path.join(basedir, os.path.join(os.path.join(MEDIA_DOWNLOAD_PATH, name[:3]), name[3:6]))
    fullpath = os.path.join(path, filename)

    if not os.path.exists(fullpath):
        try:
            os.makedirs(path)
        except OSError:
            pass

        try:
            r = requests.get(url, stream=True, timeout=5)
            if r.status_code == 200:
                with open(fullpath, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                logger.info("media display %s fetched.", fullpath)
        except ConnectionError:
            pass
        except ReadTimeout:
            pass
        except ReadTimeoutError:
            pass
