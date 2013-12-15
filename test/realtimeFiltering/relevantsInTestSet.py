__author__ = 'giacomo'

import sys, os
from CipCipPy.utils.fileManager import readQueries, readQrels

queries = readQueries(sys.argv[1])
qrels = readQrels(sys.argv[2], set(q[0] for q in queries))
filteringIdsPath = sys.argv[3]

for i, q in enumerate(queries):
    testFile = open(os.path.join(filteringIdsPath, q[0]))
    pos = 0
    for line in testFile:
        tweetId, null, text = line.partition('\t\t')
        if tweetId in qrels[int(q[0][2:])][0]:
            pos += 1
    print q, pos, len(qrels[int(q[0][2:])][0])