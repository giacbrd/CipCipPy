import sys
from CipCipPy import corpus
from CipCipPy.corpus.filters import LinkTitles

newCorpus = sys.argv[1]
oldCorpus = sys.argv[2]
outPath = sys.argv[3]

corpus.enrich(oldCorpus, newCorpus, [LinkTitles], outPath, processes = 4, overwrite=False)