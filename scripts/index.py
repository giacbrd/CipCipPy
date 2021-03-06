"""
Index all corpus and store their content in separated indexes
arguments:
    topics file
    path of the tweet statuses corpus
    path of the corpus from which extract hashtags (usually is the statuses corpus)
    path of the link titles corpus
"""

#FIXME use argparse

import sys, os
from Queue import Empty
from CipCipPy.utils.io import readQueries, topicsFileName
from CipCipPy.indexing import hashtag, linktitle, status
from CipCipPy.config import RESOURCE_PATH

queries = readQueries(sys.argv[1])
nameSuffix = "." + topicsFileName(sys.argv[1])

def index(q):
    print q
    print "link titles indexing"
    try:
        linktitle.index(sys.argv[4], 'linkTitle' + nameSuffix, tweetTime = q[3])
    except Empty:
        print "empty index, skipping!"
    print "status indexing"
    try:
        hashtag.index(sys.argv[3], 'hashtag' + nameSuffix, tweetTime = q[3], dictionary=os.path.join(RESOURCE_PATH, '1gramsGoogle'))
    except Empty:
        print "empty index, skipping!"
    try:
        status.index(sys.argv[2], 'status' + nameSuffix, tweetTime = q[3])
    except Empty:
        print "empty index, skipping!"
    print "hashtags indexing"

print "collection data indexing"
status.index(sys.argv[2], 'storedStatus', stored = True)
hashtag.index(sys.argv[3], 'storedHashtag' , stored = True, dictionary=os.path.join(RESOURCE_PATH, '1gramsGoogle'))
linktitle.index(sys.argv[4], 'storedLinkTitle', stored = True)

try:
    for q in queries:
        index(q)
except Empty:
    print "empty index, skipping!"