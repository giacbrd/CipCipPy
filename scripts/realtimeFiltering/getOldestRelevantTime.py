import sys

from CipCipPy.utils.fileManager import readQueries, readQrels


queries = readQueries(sys.argv[1])
qrels = readQrels(sys.argv[2], set(q[0] for q in queries))

for q in qrels:
    print q, min(qrels[q][0])