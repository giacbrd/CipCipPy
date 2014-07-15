"""Training set generation for real-time filtering.
For each query serialize tweet ids and corpus content previous to query time. Last content is external, e.g. link titles.
usage: <corpus directory> <output directory> <Dexter API url> <number of processes>"""
import gzip

import json
import os
import sys
import codecs
import errno
from multiprocessing import Pool

from CipCipPy.utils.fileManager import readQueries, iterTweets, topicsFileName
from CipCipPy.retrieval import getStoredValue

from CipCipPy.indexing import getIndex
from pydexter import DexterClient

corpusPath = sys.argv[1]
outPath = sys.argv[2]
dxtr = DexterClient(sys.argv[3], default_params={"lp":0.1})
processes = int(sys.argv[4])

#FIXME avoid whoosh indexes!

#_storedStatusAll = getIndex('storedStatusAll')
_storedStatus = getIndex('storedStatus')
_storedHashtag = getIndex('storedHashtag')
_storedLinkTitle = getIndex('storedLinkTitle')
#_storedNamedEntity = getIndex('storedNamedEntity')

#def getFirstStatus(indexId):
#    return getStoredValue(_storedStatusAll, indexId, 'status')
def getStatus(indexId):
    return getStoredValue(_storedStatus, indexId, 'status')
def getTitle(indexId):
    return getStoredValue(_storedLinkTitle, indexId, 'title')
def getHashtag(indexId):
    return getStoredValue(_storedHashtag, indexId, 'hashtags')

def clean(text):
    return text if text is not None else u''

def entities(text):
    spots = dxtr.spot(text)
    mentions = {}
    for spot in spots:
        for entity in spot["candidates"]:
            ent_id = entity["entity"]
            if ent_id not in mentions:
                # Don not keep entity candidates of mentions
                mentions[ent_id] = [{key: value for key, value in m.iteritems() if key != "candidates"}
                                    for m in dxtr.get_spots(ent_id) if m["linkProbability"] > 0.1]
    return spots, mentions


def generate(corpusPath, dirList, outPath):
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
                                           title, entities(status), entities(title))) + '\n'
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
    pool.apply_async(generate, [corpusPath, chunk, outPath])
pool.close()
pool.join()