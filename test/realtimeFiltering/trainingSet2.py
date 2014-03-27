"""Training set generation for real-time filtering.
For each query serialize tweet ids and corpus content previous to query time. Last content is external, e.g. link titles.
usage: <topics file> <corpus directory> <output directory> [query numbers divided by :]"""

import os
import sys
from CipCipPy.utils.fileManager import readQueries, iterTweets, topicsFileName
from CipCipPy.indexing import getIndexPath, getIndex
from CipCipPy.retrieval import getStoredValue
import codecs
import errno

queries = readQueries(sys.argv[1])
nameSuffix = "." + topicsFileName(sys.argv[1])

outPath = sys.argv[3]

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


if not os.path.exists(outPath):
    try:
        os.makedirs(outPath)
    except OSError as e:
        if e.errno == errno.EEXIST:
            print 'Error: ', e
            print 'continuing...'
        else:
            raise

for q in queries:
    dirList = os.listdir(sys.argv[2])
    outName = os.path.join(outPath, q[0])
    tempOutName = os.path.join(outPath, "TEMP_" + q[0])
    outFile = codecs.open(tempOutName, 'w', encoding='utf8')
    for fName in dirList:
        for tweet in iterTweets(os.sep.join([sys.argv[2], fName])):
            timeInt = int(tweet[0])
            if timeInt < q[3] and tweet[2] != '302':
                time = str(timeInt)
                status = getStatus(time)
                title = getTitle(time)
                annotations = getAnnotation(time)
                if status or title:
                    outFile.write(time + '\t\t' + clean(status) + '\t\t' + clean(getHashtag(time)) + '\t\t' + \
                                  clean(title).strip().replace('\t', ' ') + '\t\t' + clean(annotations) + '\n')
    outFile.close()
    os.system("tac " + tempOutName + " > " + outName)
    os.remove(tempOutName)
