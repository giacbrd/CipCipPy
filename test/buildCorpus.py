import sys

from CipCipPy import corpus

from CipCipPy.corpus.filters import HtmlUnescape


inPath = sys.argv[1]
outPath = sys.argv[2]

corpus.build([HtmlUnescape()], inPath, outPath)