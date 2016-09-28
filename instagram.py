import os
import time
import json
import requests
from requests.exceptions import ConnectionError, ReadTimeout
import shutil


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
    path = '/'.join([basedir, USER_PATH, username[:1]])
    fullpath = '/'.join([path, username]) + '.json'

    print "Loading user " + username + '...',

    cached = False
    if cache == 'disk':
        if os.path.exists(fullpath):
            with open(fullpath, 'r') as f:
                user = json.load(f)
                cached = True
                print "from cache."

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

                    with open(fullpath, 'w') as f:
                        f.write(r.content)

                user = r.json()
                print "fetched."
        except ConnectionError:
            pass
        except ReadTimeout:
            pass

    if user is None:
        print "FAILED!"

    return user


def get_media(code, basedir, cache=None):
    media = None
    path = '/'.join([basedir, MEDIA_PATH, code[:3]])
    fullpath = '/'.join([path, code]) + '.json'

    print "Loading media " + code + '...',

    cached = False
    if cache == 'disk':
        if os.path.exists(fullpath):
            with open(fullpath, 'r') as f:
                media = json.load(f)
                cached = True
                print "from cache."

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

                    with open(fullpath, 'w') as f:
                        f.write(r.content)

                media = r.json()
                print "fetched."
        except ConnectionError:
            pass
        except ReadTimeout:
            pass

    if media is None:
        print "FAILED!"

    return media


def get_location(location_id, basedir, cache=None):
    location = None
    path = '/'.join([basedir, LOCATION_PATH, location_id[:3]])
    fullpath = '/'.join([path, location_id]) + '.json'

    print "Loading location " + location_id + '...',

    cached = False
    if cache == 'disk':
        if os.path.exists(fullpath):
            with open(fullpath, 'r') as f:
                location = json.load(f)
                cached = True
                print "from cache."

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

                    with open(fullpath, 'w') as f:
                        f.write(r.content)

                location = r.json()
                print "fetched."
        except ConnectionError:
            pass
        except ReadTimeout:
            pass

    if location is None:
        print "FAILED!"

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
    path = '/'.join([basedir, IG_USER_PATH, user_id[:3]])
    fullpath = '/'.join([path, str(user_id)]) + '.json'

    print "Loading ig_user " + str(user_id) + '...',

    cached = False
    if cache == 'disk':
        if os.path.exists(fullpath):
            with open(fullpath, 'r') as f:
                ig_user = json.load(f)
                cached = True
                print "from cache."

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

                    with open(fullpath, 'w') as f:
                        f.write(r.content)

                ig_user = r.json()
                print "fetched."
        except ConnectionError:
            pass
        except ReadTimeout:
            pass

    if ig_user is None:
        print "FAILED!"

    return ig_user


def download_media(url, basedir, name):
    filename = name + '.jpg'
    path = '/'.join([basedir, MEDIA_DOWNLOAD_PATH, name[:3], name[3:6]])
    fullpath = '/'.join([path, filename])

    print "Looking for " + fullpath + "...",
    if not os.path.exists(fullpath):
        try:
            os.makedirs('/'.join([basedir, path]))
        except OSError:
            pass

        try:
            r = requests.get(url, stream=True, timeout=5)
            if r.status_code == 200:
                with open(fullpath, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                print "downloaded."
            else:
                print "FAILED!"
        except ConnectionError:
            pass
        except ReadTimeout:
            pass
    else:
        print "cached."
