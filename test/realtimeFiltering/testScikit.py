"""
Test filtering.
arguments:
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


import sys, errno, json, os

from CipCipPy.utils.fileManager import readQueries, readQrels
from CipCipPy.realtimeFiltering import SupervisedFilterer
from CipCipPy.classification.scikitClassifiers import *
from CipCipPy.classification.feature import *


#FIXME use argparse

queries = readQueries(sys.argv[1])

with open(sys.argv[2]) as ann_qfile:
    queriesAnnotated = json.load(ann_qfile)

if len(sys.argv) > 8:
    queries = [q for q in queries if q[0] in set(sys.argv[8].split(':'))]

qrels = readQrels(sys.argv[3], set(q[0] for q in queries))
dataset_path = sys.argv[4]
resultsPath = sys.argv[5]

external = False
if sys.argv[6] == 'external':
    external = True

param = sys.argv[7].split('-')

classifier, classifierParam, neg, minLinkProb, expansion_limit, annotationRule, statusFeatures, genericFeatures, \
    entityFeatures, binaryFeatures = param

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
                      [eval(feat) for feat in binaryFeatures.split('.')],
                      [eval(feat) for feat in entityFeatures.split('.')],
                      float(minLinkProb),
                      expansion_limit=float(expansion_limit))

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

results, printOut = f.get(queries, queriesAnnotated, int(neg), dataset_path,
            qrels, external, annotationFilter=True if annotationRule == 'True' else False, dumpsPath=dumpsPath)

#print printOut
#printEval(sys.argv[1], sys.argv[3], results)


#indexForPrint = whoosh.index.open_dir(getIndexPath('storedStatus'))

#writeResults(results, runName, resultsPath, indexForPrint = indexForPrint)

