#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, division
import io
from multiprocessing import cpu_count
import logging
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


PROGRESS_PER = 10000


class MultipleFileSentences(object):
    def __init__(self, directory):
        self.directory = directory
        self.tokenizer = TweetTokenizer(preserve_case=False, reduce_len=True, strip_handles=True)

    @staticmethod
    def my_json_load(f):
        content = f.read()
        try:
            data = ujson.loads(content)
        except ValueError:
            try:
                data = json.loads(content)
            except ValueError as ve:
                data = ''
                logger.warn('DECODE FAIL: %s %s', f.name, ve.message)
        return data

    def __iter__(self):
        for root, dirnames, filenames in walk(path.join(self.directory, 'p')):
            for filename in fnmatch.filter(filenames, '*.json'):
                with io.open(path.join(root, filename), 'r', encoding='utf8') as f:
                    data = self.my_json_load(f)
                    if 'media' in data and 'caption' in data['media']:
                        yield self.tokenizer.tokenize(data['media']['caption'])

        for root, dirnames, filenames in walk(path.join(self.directory, 'explore/locations')):
            for filename in fnmatch.filter(filenames, '*.json'):
                with io.open(path.join(root, filename), 'r', encoding='utf8') as f:
                    data = self.my_json_load(f)
                    if 'location' in data:
                        location = data['location']
                        if 'media' in location and 'nodes' in location['media']:
                            for i, media in enumerate(location['media']['nodes']):
                                if 'caption' in media:
                                    yield self.tokenizer.tokenize(media['caption'])
                        if 'top_posts' in location and 'nodes' in location['top_posts']:
                            for i, media in enumerate(location['top_posts']['nodes']):
                                if 'caption' in media:
                                    yield self.tokenizer.tokenize(media['caption'])


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
)
def main(in_dir, out_loc, skipgram=0, negative=5, n_workers=cpu_count(), window=10, size=200, min_count=10, nr_iter=2):
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
    sentences = MultipleFileSentences(in_dir)
    model.build_vocab(sentences, progress_per=PROGRESS_PER)
    model.train(sentences)

    model.save(out_loc)


if __name__ == '__main__':
    plac.call(main)
