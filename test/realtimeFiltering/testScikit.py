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
    parameters: classifier (R, NC), classifier parameter, number of negative samples,
        minimum link probability, annotation pre-filtering, feature extraction function names (divided by .) for twitter status,
        for generic feature extraction, for binary features.
        e.g. R-0.2-100-....-terms.bigrams-terms-hasUrl.hasMention
    [query numbers divided by :]
"""


import os
import sys, errno
from CipCipPy.evaluation.trecTools import printEval
from CipCipPy.utils.fileManager import readQueries, readQrels
from CipCipPy.realtimeFiltering import SupervisedFilterer
from CipCipPy.classification.scikitClassifiers import ADAClassifier, NCClassifier, RClassifier, LClassifier, \
    DTClassifier, KNNClassifier, RFClassifier, RocchioClassifier
from CipCipPy.classification.feature import *

#FIXME use argparse

queries = readQueries(sys.argv[1])
queriesAnnotated = readQueries(sys.argv[2])
if len(sys.argv) > 9:
    queries = [q for q in queries if q[0] in set(sys.argv[9].split(':'))]
    queriesAnnotated = [q for q in queriesAnnotated if q[0] in set(sys.argv[9].split(':'))]
assert len(queries) == len(queriesAnnotated)

qrels = readQrels(sys.argv[3], set(q[0] for q in queries))
filteringIdsPath = sys.argv[4]
trainingSetPath = sys.argv[5]
resultsPath = sys.argv[6]

external = False
if sys.argv[7] == 'external':
    external = True

param = sys.argv[8].split('-')

classifier, classifierParam, neg, minLinkProb, annotationRule, statusFeatures, genericFeatures, binaryFeatures = param
if classifier == 'NC':
    classifier = NCClassifier(shrink=float(classifierParam) if classifierParam != 'None' else None)
elif classifier == 'R':
    classifier = RClassifier(alpha=float(classifierParam))
elif classifier == 'ADA':
    classifier = ADAClassifier(estimators=int(classifierParam))
elif classifier == 'L':
    classifier = LClassifier(C=float(classifierParam))
elif classifier == 'DT':
    classifier = DTClassifier()
elif classifier == 'KNN':
    classifier = KNNClassifier()
elif classifier == 'RF':
    classifier = RFClassifier()
elif classifier == 'RO':
    classifier = RocchioClassifier(threshold=float(classifierParam))

f = SupervisedFilterer(classifier)
f.setFeatureExtractor([eval(feat) for feat in statusFeatures.split('.')],
                      [eval(feat) for feat in genericFeatures.split('.')],
                      [eval(feat) for feat in binaryFeatures.split('.')])

runName = 'run' + '-'.join(param) + ('_external' if external else '_internal')

dumpsPath = os.path.join(resultsPath, 'dumps_' + runName)
if not os.path.exists(dumpsPath):
    try:
        os.makedirs(dumpsPath)
    except OSError as e:
        if e.errno == errno.EEXIST:
            print 'Error: ', e
            print 'continuing...'
        else:
            raise

results = f.get(queries, queriesAnnotated, int(neg), trainingSetPath, filteringIdsPath,
                qrels, external, float(minLinkProb), annotationFilter = True if annotationRule=='True' else False,
                dumpsPath=dumpsPath)

printEval(sys.argv[1], sys.argv[3], results)


#indexForPrint = whoosh.index.open_dir(getIndexPath('storedStatus'))

#writeResults(results, runName, resultsPath, indexForPrint = indexForPrint)

