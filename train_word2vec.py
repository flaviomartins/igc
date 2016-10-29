#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fnmatch
import os
import sys
import json
import gensim
from nltk.tokenize import TweetTokenizer

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class SingleFileSentences(object):
    def __init__(self, filename):
        self.filename = filename
        self.tokenizer = TweetTokenizer(preserve_case=False, reduce_len=True, strip_handles=True)

    def __iter__(self):
        for line in open(self.filename):
            yield self.tokenizer.tokenize(line)


class MultipleFileSentences(object):
    def __init__(self, basedir):
        self.basedir = basedir
        self.tokenizer = TweetTokenizer(preserve_case=False, reduce_len=True, strip_handles=True)

    def __iter__(self):
        for root, dirnames, filenames in os.walk(os.path.join(self.basedir, 'p')):
            for filename in fnmatch.filter(filenames, '*.json'):
                with open(os.path.join(root, filename)) as f:
                    data = json.load(f)
                    if 'media' in data and 'caption' in data['media']:
                        yield self.tokenizer.tokenize(data['media']['caption'])

        for root, dirnames, filenames in os.walk(os.path.join(self.basedir, 'explore/locations')):
            for filename in fnmatch.filter(filenames, '*.json'):
                with open(os.path.join(root, filename)) as f:
                    data = json.load(f)
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


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: train_word2vec.py <inputfile> <modelname>"
        sys.exit(0)

    inputfile = sys.argv[1]
    modelname = sys.argv[2]
    sentences = MultipleFileSentences(inputfile)
    model = gensim.models.Word2Vec(sentences, size=200, window=10, min_count=10,
                                   workers=4, iter=5, sorted_vocab=1)
    model.save(modelname)
