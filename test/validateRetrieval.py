from CipCipPy.retrieval import Searcher
from whoosh import scoring
import sys
from CipCipPy.utils.fileManager import readQueries, writeResults, readQrels, topicsFileName
from CipCipPy.indexing import getIndexPath
from CipCipPy.evaluation import AUC, ROC
from itertools import product, permutations
import EvalJig as ej
from mb12eval import *


numOfResults = 10000 # how many tweets retrieve and filter, scores are biased on this value

### PARAMETERS ###

resultsQueryExp = (0, 5, 10, 20, 30)#(0, 5, 10, 20, 30, 50) # number of results from wich hashtags are extracted to expand the query for the final retrieval

# Weights for scores for final ranking, components are:
#   weight for text retrieval scores of the tweets status
#   weight for text retrieval scores of hashtags
#   weight for text retrieval scores of link titles
#   weight for date scores (higher if more recent)
scoreWeights = set()
def combinations_with_replacement(iterable, r):
    pool = tuple(iterable)
    n = len(pool)
    for indices in product(range(n), repeat=r):
        if sorted(indices) == list(indices):
            yield tuple(pool[i] for i in indices)
for x in combinations_with_replacement([0.4, 0.6, 0.3, 0.7, 0.2, 0.8, 0.1, 0.9, 0.], 4):
    if int(sum(x) * 100) == 100:
        scoreWeights.update(set(permutations(x)))

queries = readQueries(sys.argv[1])
nameSuffix = "." + topicsFileName(sys.argv[1])

s = Searcher('status' + nameSuffix, 'hashtag' + nameSuffix, 'linkTitle' + nameSuffix, 'storedStatus' + nameSuffix)

scorer = scoring.BM25F(K1 = 0)

jig = ej.EvalJig()
jig.add_op(ej.NumRetr())
jig.add_op(ej.NumRel())
jig.add_op(ej.RelRet())
jig.add_op(ej.AvePrec())
jig.add_op(ej.PrecAt(10))
jig.add_op(ej.PrecAt(20))
jig.add_op(ej.PrecAt(30))
jig.add_op(ej.RelString())
#FIXME il minimo valore di rilevanza deve essere un parametro
jig.minrel = 2
jig.evaldepth = 1000
jig.verbose = False

jig.add_op(ROC_Plot())

qrels = collections.defaultdict(dict)
with open(sys.argv[2]) as qrelsfile:
    for line in qrelsfile:
        topic, _, docid, rel = line.split()
        qrels[int(topic)][docid] = int(rel)

for qe in resultsQueryExp:
    for v in scoreWeights:
        results = s.get(queries, scorer, numOfResults, scoreWeights = v, resultsExpans = qe)
        run = collections.defaultdict(list)
        for q, res in results:
            q = int(q[2:])
            for r in res:
                run[q].append((float(r[1]), r[0]))
        for topic in run.iterkeys():
            if qrels.has_key(topic):
                jig.compute(topic, run[topic], qrels[topic])
        print v, r
        jig.print_scores()
        jig.comp_means()
        jig.print_means()