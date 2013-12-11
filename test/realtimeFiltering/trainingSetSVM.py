"""Training set generation for the SVM filterer.
Select neg negative samples and no positive samples for each query in results, ordering by retrieval score.
Arguments:
    neg - number of negative tweets to vectorize
    topics file
    output path for the training set
    "external" for using external information, otherwise "internal"
    [query numbers divided by :]
"""

import sys
import os
from CipCipPy.utils.fileManager import readQueries, topicsFileName
from CipCipPy.retrieval import Searcher, getStoredValue
from CipCipPy.indexing import getIndexPath, getIndex
from whoosh import scoring, index
import cPickle
from operator import itemgetter
from CipCipPy.realtimeFiltering import SVMFilterer
from CipCipPy.config import RESOURCE_PATH


neg = int(sys.argv[1])
if neg < 1:
    raise ValueError("One negative sample at least")
queries = readQueries(sys.argv[2])
nameSuffix = "." + topicsFileName(sys.argv[2])

external = False
if sys.argv[4] == 'external':
    external = True

outPath = os.path.join(sys.argv[3], str(neg) + ('_external' if external else '_internal'))

if len(sys.argv) > 5:
    queries = [q for q in queries if q[0] in set(sys.argv[5].split(':'))]

if not os.path.exists(outPath):
    os.makedirs(outPath)

scorer = scoring.BM25F(K1 = 0)

s = Searcher('status' + nameSuffix, 'hashtag' + nameSuffix, 'linkTitle' + nameSuffix, 'storedStatus', dictionary=os.path.join(RESOURCE_PATH, '1gramsGoogle'))
#if n:
#    # Retrieval without external information
#    posResults = s.get(queries, scorer, n, scoreWeights = (1., .0, .0, .0), resultsExpans = 0)

# Retrieval without external information
negResults = s.get(queries, scorer, neg, scoreWeights = (1., .0, .0, .0), resultsExpans = 0)#, complementary=True)

_storedStatus = getIndex('storedStatus')
_storedHashtag = getIndex('storedHashtag')
_storedLinkTitle = getIndex('storedLinkTitle')
_storedAnnotation = getIndex('storedAnnotations20130805')

def getStatus(indexId):
    store = getStoredValue(_storedStatus, indexId, 'status')
    return store if store else ""
def getTitle(indexId):
    store = getStoredValue(_storedLinkTitle, indexId, 'title')
    return store if store else ""
def getHashtag(indexId):
    store = getStoredValue(_storedHashtag, indexId, 'hashtags')
    return store if store else ""
def getAnnotation(indexId):
    store = getStoredValue(_storedAnnotation, indexId, 'annotations')
    return store if store else ""

featureExtract = SVMFilterer().featureExtract

queries = dict((q[0], q[1:]) for q in queries)

for qNum in queries:
#    if n:
#        posResult = sorted(posResults[qNum], key=itemgetter(1), reverse=True)
#        positives = [r[0] for r in posResult[:n]]
    negResult = sorted(negResults[qNum], key=itemgetter(1), reverse=True)
    negatives = [r[0] for r in negResult[:neg]]
#    # add the query as positive example
#    samples = ([(qNum, queryFeatureExtractor.get(queries[qNum][0]))], [])
    samples = ([], [])
    for tweetId in negatives:
        samples[1].append((tweetId, featureExtract(getStatus(tweetId) + '\t\t' + getHashtag(tweetId) + '\t\t' + \
                            getTitle(tweetId) + '\t\t' + getAnnotation(tweetId), external = external)))
    printOut = '\n' + '__________________________________________________' + '\n'
    printOut += str((qNum, queries[qNum][0], len(negResult))) + '\n'
    printOut += '\n'.join(str(p) for p in samples[1][:10])
    printOut +=  '\n-----------------------\n'
    print printOut

    cPickle.dump(samples, open(os.path.join(outPath, qNum), 'w'))