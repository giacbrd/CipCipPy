"""
Test filtering.
arguments:
    number of positive samples to find before starting classification (bootstrap phase)
    number of positive samples
    number of negative samples
    topics file
    relevance judgements
    path of ids and content per query for realtime filtering (test set)
    training set dir
    results dir
    "external" for using external information, otherwise "internal"
    [query numbers divided by :]
"""


import os
import sys
from CipCipPy.utils.fileManager import readQueries, readQrels
from CipCipPy.realtimeFiltering import Filterer

#FIXME use argparse

rulesCount = int(sys.argv[1])
n = int(sys.argv[2])
m = int(sys.argv[3])
queries = readQueries(sys.argv[4])
if len(sys.argv) > 10:
    queries = [q for q in queries if q[0] in set(sys.argv[10].split(':'))]
qrels = readQrels(sys.argv[5], set(q[0] for q in queries))
filteringIdsPath = sys.argv[6]
trainingSetPath = sys.argv[7]
resultsPath = sys.argv[8]
external = False
if sys.argv[9] == 'external':
    external = True


runName = 'run1_' + str(rulesCount) + '-' + str(n) + '-' + str(m) + ('_external' if external else '_internal')

dumpsPath = os.path.join(resultsPath, 'dumps_' + runName)
if not os.path.exists(dumpsPath):
        os.makedirs(dumpsPath)

f = Filterer()
results = f.get(queries, n, m, rulesCount, trainingSetPath, filteringIdsPath, qrels, external, dumpsPath)


#indexForPrint = whoosh.index.open_dir(getIndexPath('storedStatus'))

#writeResults(results, runName, resultsPath, indexForPrint = indexForPrint)

