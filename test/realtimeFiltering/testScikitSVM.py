"""
Test filtering.
arguments:
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
from src.realtimeFiltering import SVMFilterer

m = int(sys.argv[1])
queries = readQueries(sys.argv[2])
if len(sys.argv) > 8:
    queries = [q for q in queries if q[0] in set(sys.argv[8].split(':'))]
qrels = readQrels(sys.argv[3], set(q[0] for q in queries))
filteringIdsPath = sys.argv[4]
trainingSetPath = sys.argv[5]
resultsPath = sys.argv[6]
external = False
if sys.argv[7] == 'external':
    external = True


runName = 'runSVM_' + str(m) + ('_external' if external else '_internal')

dumpsPath = os.path.join(resultsPath, 'dumps_' + runName)
if not os.path.exists(dumpsPath):
        os.makedirs(dumpsPath)

f = SVMFilterer()
results = f.get(queries, m, trainingSetPath, filteringIdsPath, qrels, external, dumpsPath)


#indexForPrint = whoosh.index.open_dir(getIndexPath('storedStatus'))

#writeResults(results, runName, resultsPath, indexForPrint = indexForPrint)

