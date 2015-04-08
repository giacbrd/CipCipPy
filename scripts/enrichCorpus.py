import sys
from CipCipPy import corpus

newCorpus = sys.argv[1]
oldCorpus = sys.argv[2]
outPath = sys.argv[3]

corpus.enrich(oldCorpus, newCorpus, [], outPath, processes = 4, overwrite=False)