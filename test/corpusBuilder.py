from CipCipPy import corpus
import sys
from CipCipPy.corpus.filters import English2, htmlUnescape

inPath = sys.argv[1]
outPath = sys.argv[2]

corpus.build([htmlUnescape()], inPath, outPath)