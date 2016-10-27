#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import gensim
from nltk.tokenize import TweetTokenizer


class SingleFileSentences(object):
    def __init__(self, filename):
        self.filename = filename
        self.tokenizer = TweetTokenizer(preserve_case=False, reduce_len=False, strip_handles=False)

    def __iter__(self):
        for line in open(self.filename):
            yield self.tokenizer.tokenize(line)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: train_word2vec.py <inputfile> <modelname>"
        sys.exit(0)

    inputfile = sys.argv[1]
    modelname = sys.argv[2]
    sentences = SingleFileSentences(inputfile)
    model = gensim.models.Word2Vec(sentences, size=200, window=10, min_count=10,
                                   workers=4, iter=5, sorted_vocab=1)
    model.save(modelname)
