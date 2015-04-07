"""Dataset generation for real-time filtering.
usage: <corpus directory> <output directory> <Dexter API url> <number of processes>"""

import gzip, json, os, sys, errno
from multiprocessing import Pool

from CipCipPy.utils.io import iterTweets
from CipCipPy.retrieval import getStoredValue
from CipCipPy.utils.annotation import entities
from CipCipPy.indexing import getIndex

from pydexter import DexterClient

corpusPath = sys.argv[1]
outPath = sys.argv[2]
dxtr = DexterClient(sys.argv[3], default_params={"lp":0.2})
processes = int(sys.argv[4])

#FIXME avoid whoosh indexes! (consequently whoosh dependency)

_storedStatus = getIndex('storedStatus')
_storedHashtag = getIndex('storedHashtag')
_storedLinkTitle = getIndex('storedLinkTitle')
def getStatus(indexId):
    return getStoredValue(_storedStatus, indexId, 'status')
def getTitle(indexId):
    return getStoredValue(_storedLinkTitle, indexId, 'title')
def getHashtag(indexId):
    return getStoredValue(_storedHashtag, indexId, 'hashtags')

def clean(text):
    return text if text is not None else u''

def generate(corpusPath, dirList, outPath, dxtr):
    for fName in dirList:
        outData = ''
        minTime, maxTime = float("inf"), -float("inf")
        for tweet in iterTweets(os.sep.join([corpusPath, fName])):
            timeInt = int(tweet[0])
            if tweet[2] != '302':
                time = str(timeInt)
                status = getStatus(time)
                title = clean(getTitle(time)).strip().replace('\t', ' ')
                if status or title:
                    if timeInt < minTime:
                        minTime = timeInt
                    if timeInt > maxTime:
                        maxTime = timeInt
                    outData += json.dumps((timeInt, clean(status), clean(getHashtag(time)),
                                           title, entities(status, dxtr, 0.2), entities(title, dxtr, 0.2))) + '\n'
        outName = os.path.join(outPath, str(minTime)+"-"+str(maxTime))
        with gzip.open(filename=outName, mode='w') as outGzip:
            outGzip.write(outData)

if not os.path.exists(outPath):
    try:
        os.makedirs(outPath)
    except OSError as e:
        if e.errno == errno.EEXIST:
            print 'Error: ', e
            print 'continuing...'
        else:
            raise

dirList = os.listdir(corpusPath)
pool = Pool(processes)
filePerChunk = int(len(dirList) / processes) + 1
chunks =[dirList[i:i+filePerChunk] for i in range(0,len(dirList),filePerChunk)]
for chunk in chunks:
    pool.apply_async(generate, [corpusPath, chunk, outPath, dxtr])
pool.close()
pool.join()