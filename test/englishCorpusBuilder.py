from CipCipPy import corpus
import sys
from CipCipPy.corpus.filters import English2

inPath = sys.argv[1]
outPath = sys.argv[2]

corpus.build([English2()], inPath, outPath)