"""Write results from result dumps
usage: <dumps dir> <out path> <run name> [printTweets]"""

import sys
import os
import cPickle
from CipCipPy.utils.fileManager import writeResults
import whoosh.index
from CipCipPy.indexing import getIndexPath

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