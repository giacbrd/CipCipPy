"""
Test filtering.
arguments:
    number of negative samples
    topics file
    annotated topics file
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
from CipCipPy.realtimeFiltering import SupervisedFilterer
from CipCipPy.classification.scikitClassifiers import ADAClassifier


#FIXME use argparse

m = int(sys.argv[1])
queries = readQueries(sys.argv[2])
queriesAnnotated = readQueries(sys.argv[3])
if len(sys.argv) > 9:
    queries = [q for q in queries if q[0] in set(sys.argv[9].split(':'))]
    queriesAnnotated = [q for q in queriesAnnotated if q[0] in set(sys.argv[9].split(':'))]
assert len(queries) == len(queriesAnnotated)

qrels = readQrels(sys.argv[4], set(q[0] for q in queries))
filteringIdsPath = sys.argv[5]
trainingSetPath = sys.argv[6]
resultsPath = sys.argv[7]

external = False
if sys.argv[8] == 'external':
    external = True


runName = 'runADA_' + str(m) + ('_external' if external else '_internal')

dumpsPath = os.path.join(resultsPath, 'dumps_' + runName)
if not os.path.exists(dumpsPath):
        os.makedirs(dumpsPath)

f = SupervisedFilterer(ADAClassifier)
results = f.get(queries, queriesAnnotated, m, trainingSetPath, filteringIdsPath,
                qrels, external, annotationFilter = True, dumpsPath = dumpsPath)


#indexForPrint = whoosh.index.open_dir(getIndexPath('storedStatus'))

#writeResults(results, runName, resultsPath, indexForPrint = indexForPrint)

