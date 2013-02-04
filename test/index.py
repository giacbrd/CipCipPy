"""
Index all corpus and store their content in separated inndexes
arguments:
    topics file
    path of the tweet statuses corpus
    path of the corpus from which extract hashtags (usually is the statuses corpus)
    path of the link titles corpus
    path of the tweet named entities corpus
"""

#FIXME usa argparse ovunque

from CipCipPy.utils.fileManager import readQueries, topicsFileName
from CipCipPy.indexing import hashtag, linkTitle, status, namedEntity
import sys
from Queue import Empty

queries = readQueries(sys.argv[1])
nameSuffix = "." + topicsFileName(sys.argv[1])

def index(q):
    print q
    print "link titles indexing"
    try:
        linkTitle.index(sys.argv[4], 'linkTitle' + nameSuffix, tweetTime = q[3])
    except Empty:
        print "empty index, skipping!"
    print "status indexing"
    try:
        status.index(sys.argv[2], 'status' + nameSuffix, tweetTime = q[3])
    except Empty:
        print "empty index, skipping!"
    print "hashtags indexing"
    try:
        hashtag.index(sys.argv[3], 'hashtag' + nameSuffix, tweetTime = q[3])
    except Empty:
        print "empty index, skipping!"

print "collection data indexing"
status.index(sys.argv[2], 'storedStatus', stored = True)
linkTitle.index(sys.argv[4], 'storedLinkTitle', stored = True)
hashtag.index(sys.argv[3], 'storedHashtag' , stored = True)
namedEntity.index(sys.argv[5], 'storedNamedEntity', stored = True, overwrite = False)

try:
    for q in queries:
        index(q)
except Empty:
    print "empty index, skipping!"
