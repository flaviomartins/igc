#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from builtins import object
from builtins import zip

import plac
import gzip
import io
try:
    import ujson
except ImportError:
    import json as ujson
import json

import logging
import itertools
import multiprocessing
from os import path

# fails to import scandir < 3.5
try:
    from os import scandir, walk
except ImportError:
    from scandir import scandir, walk
import fnmatch

from gensim import utils
import instagram as ig

logger = logging.getLogger(__name__)


class JsonDirPosts(object):
    def __init__(self, in_dir, out_dir, n_workers=multiprocessing.cpu_count()-1, job_size=1):
        self.directory = in_dir
        self.out_dir = out_dir
        self.n_workers = n_workers
        self.job_size = job_size

    def __iter__(self):
        files = iter_files(self.directory)
        posts = 0
        pool = multiprocessing.Pool(self.n_workers)
        # process the corpus in smaller chunks of docs, because multiprocessing.Pool
        # is dumb and would load the entire input into RAM at once...
        for group in utils.chunkize(files, chunksize=self.job_size * self.n_workers, maxsize=1):
            for result in pool.imap(process_file, zip(group, itertools.repeat(self.out_dir))):
                posts += 1
                yield result
        pool.terminate()

        logger.info("finished iterating over corpus of %i documents", posts)
        self.length = posts  # cache corpus length


def iter_files(directory):
    for root, dirnames, filenames in walk(directory):
        for filename in fnmatch.filter(filenames, '*.json*'):
            yield path.join(root, filename)


def process_file(args):
    filepath, out_dir = args
    try:
        if filepath.endswith('.gz'):
            f = gzip.open(filepath)
        else:
            f = io.open(filepath, 'rt', encoding='utf-8')
    except IOError:
        logger.warning('COULD NOT READ: %s', filepath)
        return (False, filepath)

    try:
        data = ujson.load(f)
    except ValueError:
        try:
            data = json.load(f)
        except ValueError as ve:
            logger.warning('DECODE FAIL: %s %s', filepath, ve.message)
            return (False, filepath)
    if 'media' in data:
        media = data['media']
        if 'id' in media and 'display_src' in media:
            ig.download_media(media['display_src'], out_dir, media['id'])
    f.close()
    return (True, filepath)


@plac.annotations(
    in_dir=("Location of input directory"),
    out_dir=("Location of output directory"),
    n_workers=("Number of workers", "option", "n", int),
    job_size=("Job size in number of lines", "option", "j", int)
)
def main(in_dir, out_dir, n_workers=multiprocessing.cpu_count()-1, job_size=1):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    for result in JsonDirPosts(in_dir, out_dir, n_workers, job_size):
        if result[0] is False:
            logger.error("COULD NOT DOWNLOAD %s", result[1])


if __name__ == '__main__':
    plac.call(main)
