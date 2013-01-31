from CipCipPy.retrieval import Searcher
from whoosh import scoring
import sys
from CipCipPy.utils.fileManager import readQueries, writeResults, readQrels
from CipCipPy.indexing import getIndexPath
from CipCipPy.evaluation import AUC, ROC
from itertools import product, permutations

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
qrels = readQrels(sys.argv[2], set(q[0] for q in queries))

s = Searcher('statusValidation', 'hashtagValidation', 'linkTitleValidation', 'storedStatus')

scorer = scoring.BM25F(K1 = 0)

best = (0.5,)

for r in resultsQueryExp:
    for v in scoreWeights:
        results = s.get(queries, scorer, numOfResults, scoreWeights = v, resultsExpans = r)
        #FIXME usa script ufficiali di TREC
        curves = ROC(results, qrels)
        areas = 0.
        for curve in curves:
            areas += AUC(curve)
        eval = (areas / len(curves), v, r)
        print eval
        if eval[0] > best[0]:
            best = eval
print 'best: ', best

