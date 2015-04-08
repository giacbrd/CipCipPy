"""Evaluate results with TREC tools
usage: <dumps dir> <topicsFile> <qrelsFile>"""

import sys, os, cPickle

from CipCipPy.evaluation.trec import printEval

inPath = sys.argv[1]
topicsPath = sys.argv[2]
qrelsPath = sys.argv[3]

results = {}

for q in os.listdir(inPath):
    results[q] = cPickle.load(open(os.path.join(inPath, q)))

printEval(topicsPath, qrelsPath, results)