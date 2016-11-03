#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division
import io
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import logging
from toolz import partition_all
from itertools import chain
from os import path
# fails to import scandir < 3.5
try:
    from os import scandir, walk
except ImportError:
    from scandir import scandir, walk
import fnmatch

import plac
try:
    import ujson
except ImportError:
    import json as ujson
import json
from gensim.models import Word2Vec
from nltk.tokenize import TweetTokenizer

logger = logging.getLogger(__name__)


TOKENIZER = TweetTokenizer(preserve_case=False, reduce_len=True, strip_handles=True)


class MultipleFileSentences(object):
    def __init__(self, directory, n_workers=cpu_count(), job_size=10000):
        self.directory = directory
        self.n_workers = n_workers
        self.job_size = job_size

    def __iter__(self):
        jobs = partition_all(self.job_size, chain(iter_jsons(path.join(self.directory, 'p')),
                                                  iter_jsons(path.join(self.directory, 'explore/locations'))))
        with ProcessPoolExecutor(max_workers=self.n_workers) as executor:
            futures = []
            for j, job in enumerate(jobs):
                futures.append(executor.submit(process_job, job))
                if j % self.n_workers == 0:
                    for f in as_completed(futures):
                        results = f.result()
                        for result in results:
                            if result is not None:
                                yield result
                    futures = []
            for f in as_completed(futures):
                results = f.result()
                for result in results:
                    if result is not None:
                        yield result


def iter_jsons(directory):
    for root, dirnames, filenames in walk(directory):
        for filename in fnmatch.filter(filenames, '*.json'):
            yield path.join(root, filename)


def process_job(job):
    results = []
    for filepath in job:
        result = process_file(filepath)
        if result is not None:
            results.append(result)
    return results


def process_file(filepath):
    with io.open(filepath, 'r', encoding='utf8') as f:
        content = f.read()
    try:
        data = ujson.loads(content)
    except ValueError:
        try:
            data = json.loads(content)
        except ValueError as ve:
            data = ''
            logger.warn('DECODE FAIL: %s %s', f.name, ve.message)
    if 'media' in data and 'caption' in data['media']:
        return TOKENIZER.tokenize(data['media']['caption'])
    if 'location' in data:
        location = data['location']
        if 'media' in location and 'nodes' in location['media']:
            for i, media in enumerate(location['media']['nodes']):
                if 'caption' in media:
                    return TOKENIZER.tokenize(media['caption'])
        if 'top_posts' in location and 'nodes' in location['top_posts']:
            for i, media in enumerate(location['top_posts']['nodes']):
                if 'caption' in media:
                    return TOKENIZER.tokenize(media['caption'])


@plac.annotations(
    in_dir=("Location of input directory"),
    out_loc=("Location of output file"),
    skipgram=("By default (sg=0), CBOW is used. Otherwise (sg=1), skip-gram is employed.", "option", "sg", int),
    n_workers=("Number of workers", "option", "n", int),
    size=("Dimension of the word vectors", "option", "d", int),
    window=("Context window size", "option", "w", int),
    min_count=("Min count", "option", "m", int),
    negative=("Number of negative samples", "option", "g", int),
    nr_iter=("Number of iterations", "option", "i", int),
    job_size=("Job size in number of lines", "option", "j", int),
)
def main(in_dir, out_loc, skipgram=0, negative=5, n_workers=cpu_count(), window=10, size=200, min_count=10, nr_iter=2, job_size=5000):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    model = Word2Vec(
        size=size,
        sg=skipgram,
        window=window,
        min_count=min_count,
        workers=n_workers,
        sample=1e-5,
        negative=negative,
        iter=nr_iter
    )
    sentences = MultipleFileSentences(in_dir, n_workers, job_size)
    model.build_vocab(sentences, progress_per=10000)
    model.train(sentences)

    model.save(out_loc)


if __name__ == '__main__':
    plac.call(main)
