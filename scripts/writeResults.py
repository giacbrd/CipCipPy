"""Write results from result dumps
usage: <dumps dir> <out path> <run name> [printTweets]"""

import sys, os, cPickle

from CipCipPy.utils.io import writeResults
from CipCipPy.indexing import getIndexPath

import whoosh.index

inPath = sys.argv[1]
outPath = sys.argv[2]
runName = sys.argv[3]
indexForPrint = None
if len(sys.argv) > 4 and sys.argv[4] == 'printTweets':
    indexForPrint = whoosh.index.open_dir(getIndexPath('storedStatus'))

results = {}

for q in os.listdir(inPath):
    results[q] = cPickle.load(open(os.path.join(inPath, q)))

writeResults(results, runName, outPath, indexForPrint = indexForPrint)