"""Select first n and last m tweets as positive and negative sample for each query in results, ordering by retrieval score.
Arguments:
    n - first relevant tweets to vectorize 
    m - first less relevant tweets to vectorize
    topics file
    output path for the training set
    "external" for using external information, otherwise "internal"
    [query numbers divided by :]
"""

import sys
import os
from CipCipPy.utils.fileManager import readQueries, topicsFileName
from CipCipPy.retrieval import Searcher, getStoredValue
from CipCipPy.indexing import getIndexPath
from whoosh import scoring, index
import cPickle
from operator import itemgetter
from CipCipPy.realtimeFiltering.feature import featureExtractText, queryFeatureExtractor

n = int(sys.argv[1])
m = int(sys.argv[2])
queries = readQueries(sys.argv[3])
nameSuffix = "." + topicsFileName(sys.argv[3])

external = False
if sys.argv[5] == 'external':
    external = True

outPath = os.path.join(sys.argv[4], str(n) + '-' + str(m) + ('_external' if external else '_internal'))

if len(sys.argv) > 6:
    queries = [q for q in queries if q[0] in set(sys.argv[6].split(':'))]

if not os.path.exists(outPath):
    os.makedirs(outPath)

scorer = scoring.BM25F(K1 = 0)

if n:
    s = Searcher('status' + nameSuffix, 'hashtag' + nameSuffix, 'linkTitle' + nameSuffix, 'storedStatus')
    # Retrieval without external information
    posResults = s.get(queries, scorer, n, scoreWeights = (1., .0, .0, .0), resultsExpans = 0)
if m:
    s = Searcher('status' + nameSuffix, 'hashtag' + nameSuffix, 'linkTitle' + nameSuffix, 'storedStatus')
    # Retrieval without external information
    negResults = s.get(queries, scorer, m, scoreWeights = (1., .0, .0, .0), resultsExpans = 0, complementary=True)

_storedStatus = index.open_dir(getIndexPath('storedStatus')).searcher()
_storedHashtag = index.open_dir(getIndexPath('storedHashtag')).searcher()
_storedLinkTitle = index.open_dir(getIndexPath('storedLinkTitle')).searcher()
_storedNamedEntity = index.open_dir(getIndexPath('storedNamedEntity')).searcher()

def getStatus(indexId):
    store = getStoredValue(_storedStatus, indexId, 'status')
    return store if store else ""
def getTitle(indexId):
    store = getStoredValue(_storedLinkTitle, indexId, 'title')
    return store if store else ""
def getHashtag(indexId):
    store = getStoredValue(_storedHashtag, indexId, 'hashtags')
    return store if store else ""
def getNE(indexId):
    store = getStoredValue(_storedNamedEntity, indexId, 'namedEntities')
    return store if store else ""

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
    # FIXME la query andrebbe aggiunta nel Filterer non qua
    # add the query as positive example
    samples = ([(qNum, queryFeatureExtractor.get(queries[qNum][0]))], [])
    for i in (0, 1):
        for tweetId in (positives if i == 0 else negatives):
            samples[i].append((tweetId, featureExtractText(getStatus(tweetId) + '\t\t' + getHashtag(tweetId) + '\t\t' + getNE(tweetId) + '\t\t' + getTitle(tweetId), queries[qNum][0], external = external)))
    printOut = '__________________________________________________' + '\n'
    printOut += str((qNum, len(posResult), len(negResult))) + '\n'
    for i in (0, 1):
        printOut += '\n'.join(str(p) for p in samples[i][:10])
        printOut +=  '\n-----------------------\n'
    print printOut

    cPickle.dump(samples, open(os.path.join(outPath, qNum), 'w'))