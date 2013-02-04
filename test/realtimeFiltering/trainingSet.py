"""Select first n and last m tweets as positive and negative sample for each query in results, ordering by retrieval score.
Arguments:
    n - first relevant tweets to vectorize 
    m - first less relevant tweets to vectorize
    topics file
    output path for the training set
    [query numbers divided by :]
"""

import sys
import os
from CipCipPy.utils.fileManager import readQueries, topicsFileName
from CipCipPy.retrieval import Searcher
from whoosh import scoring
import cPickle
from operator import itemgetter
from realtimeFiltering.feature import featureExtractId, _queryFeatureExtractor

n = int(sys.argv[1])
m = int(sys.argv[2])
queries = readQueries(sys.argv[3])
nameSuffix = "." + topicsFileName(sys.argv[3])
outPath = os.path.join(sys.argv[4], str(n) + '-' + str(m))

if not os.path.exists(outPath):
    os.makedirs(outPath)

scorer = scoring.BM25F(K1 = 0)

if n:
    s = Searcher('status' + nameSuffix, 'hashtag' + nameSuffix, 'linkTitle' + nameSuffix, 'storedStatus' + nameSuffix)
    posResults = s.get(queries, scorer, n, scoreWeights = (1., .0, .0, .0), resultsExpans = 0)
if m:
    s = Searcher('status' + nameSuffix, 'hashtag' + nameSuffix, 'linkTitle' + nameSuffix, 'storedStatus' + nameSuffix)
    negResults = s.get(queries, scorer, m, scoreWeights = (1., .0, .0, .0), resultsExpans = 0, complementary=True)

queries = dict((q[0], q[1:]) for q in queries)

for qNum in queries:
    positives = []
    negatives = []
    if n:
        posResult = sorted(posResults[qNum], key=itemgetter(1), reverse=True)
        positives = [r[0] for r in posResult[:n]]
    if m:
        negResult = sorted(negResults[qNum], key=itemgetter(1), reverse=True)
        negatives = [r[0] for r in negResult[:m]]
    # add the query as positive example
    samples = ([(qNum, _queryFeatureExtractor.get(queries[qNum][0]))], [])
    for i in (0, 1):
        for tweetId in (positives if i == 0 else negatives):
            samples[i].append((tweetId, featureExtractId(tweetId, queries[qNum][0])))
    print '__________________________________________________'
    print qNum, len(posResult), len(negResult)
    for i in (0, 1):
        for p in samples[i]:
            print p
        print '-----------------------'

    cPickle.dump(samples, open(os.path.join(outPath, qNum), 'w'))