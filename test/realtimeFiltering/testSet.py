"""Test set generation for real-time filtering.
For each query serialize tweet ids and corpus content in the time range. Last content is external, e.g. link titles.
usage: <topics file> <corpus directory> <output directory> [query numbers divided by :]"""

import os
import sys
from CipCipPy.utils.fileManager import readQueries, iterTweets, topicsFileName
from CipCipPy.indexing import getIndexPath, getIndex
from CipCipPy.retrieval import getStoredValue
import codecs

queries = readQueries(sys.argv[1])
nameSuffix = "." + topicsFileName(sys.argv[1])

#_storedStatusAll = getIndex('storedStatusAll')
_storedStatus = getIndex('storedStatus')
_storedHashtag = getIndex('storedHashtag')
_storedLinkTitle = getIndex('storedLinkTitle')
_storedAnnotation = getIndex('storedAnnotations20130805')
#_storedNamedEntity = getIndex('storedNamedEntity')

#def getFirstStatus(indexId):
#    return getStoredValue(_storedStatusAll, indexId, 'status')
def getStatus(indexId):
    return getStoredValue(_storedStatus, indexId, 'status')
def getTitle(indexId):
    return getStoredValue(_storedLinkTitle, indexId, 'title')
def getHashtag(indexId):
    return getStoredValue(_storedHashtag, indexId, 'hashtags')
def getAnnotation(indexId):
    store = getStoredValue(_storedAnnotation, indexId, 'annotations')
    return store if store else ""
#def getNE(indexId):
#    return getStoredValue(_storedNamedEntity, indexId, 'namedEntities')

if len(sys.argv) > 4:
    queries = [q for q in queries if q[0] in set(sys.argv[4].split(':'))]

def clean(text):
    return text if text is not None else u''

for q in queries:
    dirList = os.listdir(sys.argv[2])
    outFile = codecs.open(os.path.join(sys.argv[3], q[0]), 'w', encoding='utf8')
    for fName in dirList:
        for tweet in iterTweets(os.sep.join([sys.argv[2], fName])):
            timeInt = int(tweet[0])
            if timeInt >= q[3] and timeInt <= q[4] and tweet[2] != '302':
                time = str(timeInt)
                status = getStatus(time)
                title = getTitle(time).strip()
                annotations = getAnnotation(time)
                if status or title:
                    outFile.write(time + '\t\t' + clean(status) + '\t\t' + clean(getHashtag(time)) + '\t\t' + \
                                  clean(title) + '\t\t' + clean(annotations) + '\n')
