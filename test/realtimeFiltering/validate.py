"""
arguments:
    validation topics file
    relevance judgements
    path of ids and content per query (test set) for realtime filtering
    training set dir
    "external" for using external information, otherwise internal"
    parameters: rulesCount-posTrainCut-negTrainCut. e.g. 10-1-100:10-2-200:10-5-100:10-5-1000
"""


import os
import sys
from CipCipPy.classification.scikitNaiveBayes import TrainingSet,NBClassifier
from CipCipPy.utils.fileManager import readQueries, readQrels
import cPickle
from CipCipPy.evaluation import T11SU, F1
from CipCipPy.classification.feature import terms
from realtimeFiltering import Filterer
from realtimeFiltering.feature import featureExtractText

queries = readQueries(sys.argv[1])
qrels = readQrels(sys.argv[2], set(q[0] for q in queries))
filteringIdsPath = sys.argv[3]
trainingSetPath = sys.argv[4]
external = False
if sys.argv[5] == 'external':
    external = True
parameters = set(tuple(c.split('-')) for c in sys.argv[6].split(':'))

def cleanUtf(features):
    cleanedFeatures = []
    for feat in features:
        feat = feat.encode('ascii', 'ignore')
        if feat:
            cleanedFeatures.append(feat)
    return cleanedFeatures

def intersect(query, text):
    return len(set(terms(query)) & set(terms(text)))

f = Filterer()

for param in parameters:
    rulesCount, n, m = [int(p) for p in param]
    results = f.get(queries, n, m, rulesCount, trainingSetPath, filteringIdsPath, qrels, external)
    T11SUs = T11SU(results, qrels)
    F1s = F1(results, qrels)
    print 'parameters:', param
    print 'T11SU', sum(T11SUs) / float(len(T11SUs)), T11SUs
    print 'F1', sum(F1s) / float(len(F1s)), F1s