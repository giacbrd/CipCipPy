"""
arguments:
    validation topics file
    relevance judgements
    path of ids and content per query (test set) for realtime filtering
    training set dir
    "external" for using external information, otherwise internal"
    parameters: rulesCount-posTrainCut-negTrainCut. e.g. 10-1-100:10-2-200:10-5-100:10-5-1000
"""

import sys
from CipCipPy.utils.fileManager import readQueries, readQrels
from CipCipPy.evaluation import T11SU, F1
from CipCipPy.classification.feature import terms
from CipCipPy.realtimeFiltering import Filterer
from mb12filteval import *
import EvalJig as ej

queries = readQueries(sys.argv[1])

qrels2 = readQrels(sys.argv[2], set(q[0] for q in queries))
filteringIdsPath = sys.argv[3]
trainingSetPath = sys.argv[4]
external = False
if sys.argv[5] == 'external':
    external = True
parameters = set(tuple(c.split('-')) for c in sys.argv[6].split(':'))

def cleanUtf(features):
    cleanedFeatures = []
    for feat in features:
        feat = feat.encode('ascii', 'replace')
        if feat:
            cleanedFeatures.append(feat)
    return cleanedFeatures

def intersect(query, text):
    return len(set(terms(query)) & set(terms(text)))

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

f = Filterer()

# Identify query tweets from the topic file
qtweets = dict()
tops = bs(open(sys.argv[1]))
for t in tops.find_all('querytweettime'):
    tnum = t.parent.num.text.strip()
    tnum = re.search(r'0*(\d+)$', tnum).group(1)
    qtweets[tnum] = t.text.strip()

# Read in relevance judgments, dropping the querytweet
qrels = collections.defaultdict(dict)
with open(sys.argv[2]) as qrelsfile:
    for line in qrelsfile:
        topic, _, docid, rel = line.split()
        if topic not in qtweets:
            continue
        if docid == qtweets[topic]:
            continue
        qrels[topic][docid] = int(rel)


for param in parameters:
    rulesCount, n, m = [int(p) for p in param]
    results = f.get(queries, n, m, rulesCount, trainingSetPath, filteringIdsPath, qrels2, external)

    run = collections.defaultdict(list)
    for q, res in results.iteritems():
        q = q.lstrip('MB0')
        for r in res:
            score, retrieve = r[1].split('\t')
            if retrieve == 'no':
                continue
            if r[0] == qtweets[q]:
                continue
            run[topic].append((float(score), r[0]))

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

    jig.print_scores()
    jig.comp_means()
    jig.print_means()

    # T11SUs = T11SU(results, qrels)
    # F1s = F1(results, qrels)
    # print 'parameters:', param
    # print 'T11SU', sum(T11SUs) / float(len(T11SUs)), T11SUs
    # print 'F1', sum(F1s) / float(len(F1s)), F1s