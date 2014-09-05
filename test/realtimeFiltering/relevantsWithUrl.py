__author__ = 'giacomo'

import sys
import os

from CipCipPy.utils.fileManager import readQueries, readQrels, dataset_iter
from CipCipPy.classification.feature import hasUrl


queries = readQueries(sys.argv[1])
qrels = readQrels(sys.argv[2], set(q[0] for q in queries))
datasetPath = sys.argv[3]

pos_tweets = set()

for i, q in enumerate(queries):
    if int(q[0][2:]) not in qrels:
        continue
    pos_tweets += qrels[int(q[0][2:])][0]


total = 0
with_urls = 0

for tweet in dataset_iter(datasetPath, -float("inf"), float("inf")):
    if int(tweet[0]) in pos_tweets:
        if hasUrl(tweet[1]):
            with_urls += 1
        total += 1

print with_urls, total