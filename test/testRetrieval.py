"""Retrieve results"""

from CipCipPy.retrieval import Searcher
import whoosh.index
from whoosh import scoring
import sys
from CipCipPy.utils.fileManager import readQueries, writeResults
from CipCipPy.indexing import getIndexPath
from CipCipPy.config import RESOURCE_PATH
import os

# how many tweets retrieve and filter, scores are biased on this value
numOfResults = 10000

### PARAMETERS ###

# number of results from wich hashtags are extracted to expand the query for the final retrieval
resultsQueryExp = (30,)#(0, 5, 10, 20, 30, 50)

# Weights for scores for final ranking, components are:
#   weight for text retrieval scores of the tweets status
#   weight for text retrieval scores of hashtags
#   weight for text retrieval scores of link titles
#   weight for date scores (higher if more recent)
scoreWeights = ((0.6, 0.4/3, 0.4/3, 0.4/3),)#(
#(0, 1., 0, 0, 0), (0, 0.6, 0, 0, 0.4), (0.4, 0.6, 0, 0, 0), (0.2, 0.6, 0, 0, 0.2), (0, 0.6, 0.4/3, 0.4/3, 0.4/3),
# (0.4/3, 0.6, 0.4/3, 0.4/3, 0), (0.1, 0.6, 0.1, 0.1, 0.1), (0.0, 0.6, 0.2, 0.0, 0.2), (0.0, 0.6, 0.2, 0.2, 0))

# minimum score a tweet must have to appear in the results, it is biased on the number of results
thresholds = (0.04,)#(0.0,0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09, 0.1, 0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,
# 0.19, 0.2, 0.21,0.22,0.23,0.24,0.25,0.26,0.27,0.28,0.29, 0.3, 0.4, 0.5)

runName = 'run1_'

queries = readQueries(sys.argv[1])

s = Searcher('status', 'hashtag', 'linkTitle', 'storedValues', dictionary=os.path.join(RESOURCE_PATH, '1gramsGoogle'))

scorer = scoring.BM25F(K1 = 0)

indexForPrint = whoosh.index.open_dir(getIndexPath('storedValues'))

for r in resultsQueryExp:
    for v in scoreWeights:
        for t in thresholds:
            results = s.get([q[1:] for q in queries], scorer, numOfResults, scoreWeights = v, resultsExpans = r, threshold = t)
            writeResults([q[0] for q in queries],
                  results,
                  runName + '%.2f-%d_%.2f-%.2f-%.2f-%.2f' % (t, r, v[0], v[1], v[2], v[3]),
                  sys.argv[2],
                  indexForPrint = indexForPrint)

