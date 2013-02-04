"""For each query serialize tweet ids and corpus content in the time range. Last content is external, like link titles.
usage: <topics file> <corpus directory> <output directory> [query numbers divided by :]"""

import os
import sys
from CipCipPy.utils.fileManager import readQueries, iterTweets, topicsFileName
from CipCipPy.indexing import getIndexPath
from CipCipPy.retrieval import getStoredValue
import whoosh.index

queries = readQueries(sys.argv[1])
nameSuffix = "." + topicsFileName(sys.argv[1])

_storedStatus = whoosh.index.open_dir(getIndexPath('storedStatus' + nameSuffix)).searcher()
_storedHashtag = whoosh.index.open_dir(getIndexPath('storedHashtag' + nameSuffix)).searcher()
_storedLinkTitle = whoosh.index.open_dir(getIndexPath('storedLinkTitle' + nameSuffix)).searcher()
_storedNamedEntity = whoosh.index.open_dir(getIndexPath('storedNamedEntity' + nameSuffix)).searcher()

def getStatus(indexId):
    return getStoredValue(_storedStatus, indexId, 'status' + nameSuffix)
def getTitle(indexId):
    return getStoredValue(_storedLinkTitle, indexId, 'title' + nameSuffix)
def getHashtag(indexId):
    return getStoredValue(_storedHashtag, indexId, 'hashtags' + nameSuffix)
def getNE(indexId):
    return getStoredValue(_storedNamedEntity, indexId, 'namedEntities' + nameSuffix)

if len(sys.argv) > 4:
    queries = [q for q in queries if q[0] in set(sys.argv[4].split(':'))]

def clean(text):
    return text.encode('ascii', 'replace') if text != None else ''

for q in queries:
    dirList = os.listdir(sys.argv[2])
    outFile = open(os.path.join(sys.argv[3], q[0]), 'w')
    for fName in dirList:
        for tweet in iterTweets(os.sep.join([sys.argv[2], fName])):
            time = int(tweet[0])
            if time >= q[3] and time <= q[4] and tweet[2] != '302':
                time = str(time)
                status = getStatus(time)
                title = getTitle(time)
                if status or title:
                    outFile.write(time + '\t\t' + clean(status) + '\t\t' + clean(getHashtag(time)) + '\t\t' + clean(getNE(time)) + '\t\t' + clean(title) + '\n')
