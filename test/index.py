from CipCipPy.utils.fileManager import readQueries
from CipCipPy.indexing import hashtag, linkTitle, status, namedEntity
import sys
from Queue import Empty

def index(q):
    print q
    print "link titles indexing"
    try:
        linkTitle.index(sys.argv[4], 'linkTitle', tweetTime = q[3])
    except Empty:
        print "empty index, skipping!"
    print "status indexing"
    try:
        status.index(sys.argv[2], 'status', tweetTime = q[3])
    except Empty:
        print "empty index, skipping!"
    print "hashtags indexing"
    try:
        hashtag.index(sys.argv[3], 'hashtag', tweetTime = q[3])
    except Empty:
        print "empty index, skipping!"

queries = readQueries(sys.argv[1])

print "collection data indexing"
status.index(sys.argv[2], 'storedStatus', stored = True)
linkTitle.index(sys.argv[4], 'storedLinkTitle', stored = True)
hashtag.index(sys.argv[3], 'storedHashtag', stored = True)
namedEntity.index(sys.argv[5], 'storedNamedEntity', stored = True)

try:
    for q in queries:
        index(q)
except Empty:
    print "empty index, skipping!"
