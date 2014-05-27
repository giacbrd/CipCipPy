"""
arguments:
    validation topics file
    validation annotated topics
    relevance judgements
    path of ids and content per query (test set) for realtime filtering
    training set dir
    "external" for using external information, otherwise internal"
    parameters: classifier (R, NC), classifier parameter, number of negative samples,
        minimum link probability, annotation pre-filtering, feature extraction function names (divided by .) for twitter status,
        for generic feature extraction, for binary features.
        e.g. R-0.1:0.2-10:100-....-terms.bigrams-terms-hasUrl.hasMention
    [query numbers divided by :]
"""

import sys, collections, re
from CipCipPy.classification.scikitClassifiers import ADAClassifier
from CipCipPy.utils.fileManager import readQueries, readQrels
from CipCipPy.evaluation import T11SU, F1
from CipCipPy.classification.feature import terms
from CipCipPy.realtimeFiltering import SupervisedFilterer
from mb12filteval import *
import EvalJig as ej
import itertools
from CipCipPy.classification.scikitClassifiers import NCClassifier, RClassifier, LClassifier, DTClassifier, KNNClassifier, RFClassifier, RocchioClassifier
from CipCipPy.classification.feature import *

queries = readQueries(sys.argv[1])
queriesAnnotated = readQueries(sys.argv[2])
assert len(queries) == len(queriesAnnotated)

qrels2 = readQrels(sys.argv[3], set(q[0] for q in queries))
filteringIdsPath = sys.argv[4]
trainingSetPath = sys.argv[5]
external = False
if sys.argv[6] == 'external':
    external = True
parameters = tuple(tuple(c.split(':')) for c in sys.argv[7].split('-'))


jig = FilterJig()
jig.add_op(ej.NumRetr())
jig.add_op(ej.NumRel())
jig.add_op(ej.RelRet())
jig.minrel = 1
jig.verbose = False
jig.add_op(Precision())
jig.add_op(Recall())
jig.add_op(Fb(0.5))
jig.add_op(T11SU())

# Identify query tweets from the topic file
qtweets = dict()
tops = bs(open(sys.argv[1]))
for t in tops.find_all('querytweettime'):
    tnum = t.parent.num.text.strip()
    tnum = re.search(r'0*(\d+)$', tnum).group(1)
    qtweets[tnum] = t.text.strip()

# Read in relevance judgments, dropping the querytweet
qrels = collections.defaultdict(dict)
with open(sys.argv[3]) as qrelsfile:
    for line in qrelsfile:
        topic, _, docid, rel = line.split()
        if topic not in qtweets:
            continue
        if docid == qtweets[topic]:
            continue
        qrels[topic][docid] = int(rel)


for param in list(itertools.product(*parameters)):

    #######  EDIT  ###########################################

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

    results, printOut = f.get(queries, queriesAnnotated, int(neg), trainingSetPath, filteringIdsPath,
                qrels2, external, float(minLinkProb), annotationFilter=True if annotationRule == 'True' else False)

    ##########################################################

    run = collections.defaultdict(list)
    for q, res in results.iteritems():
        q = q.lstrip('MB0')
        for r in res:
            score, retrieve = r[1].split('\t')
            if retrieve == 'no':
                continue
            if r[0] == qtweets[q]:
                continue
            run[q].append((float(score), r[0]))

    for topic in qrels.iterkeys():
        jig.zero(topic)
        num_rel = sum(1 for rel in qrels[topic].values() if rel >= jig.minrel)
        if num_rel == 0:
            warn("Topic "+topic+" has no relevant documents")
            continue
        if run.has_key(topic):
            jig.compute(topic, run[topic], qrels[topic])
        else:
            jig.compute(topic, [], qrels[topic])

    print printOut

    print param
    jig.print_scores()
    jig.comp_means()
    jig.print_means()


    # Using CipCipPy evaluation tools
    # T11SUs = T11SU(results, qrels)
    # F1s = F1(results, qrels)
    # print 'parameters:', param
    # print 'T11SU', sum(T11SUs) / float(len(T11SUs)), T11SUs
    # print 'F1', sum(F1s) / float(len(F1s)), F1s