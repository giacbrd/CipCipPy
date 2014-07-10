"""Training set generation for real-time filtering.
For each query serialize tweet ids and corpus content previous to query time. Last content is external, e.g. link titles.
usage: <corpus directory> <output directory> <Dexter API url>"""

import json
import os
import sys
import codecs
import errno

from CipCipPy.utils.fileManager import readQueries, iterTweets, topicsFileName
from CipCipPy.retrieval import getStoredValue

from CipCipPy.indexing import getIndex
from pydexter import DexterClient


outPath = sys.argv[2]

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

dxtr = DexterClient(sys.argv[3], default_params={"lp":0.1})

def entities(text):
    spots = dxtr.spot(text)
    mentions = {}
    for spot in spots:
        for entity in spot["candidates"]:
            ent_id = entity["entity"]
            if ent_id not in mentions:
                mentions[ent_id] = dxtr.get_spots(ent_id)
    return spots, mentions


dirList = os.listdir(sys.argv[1])
for fName in dirList:
    outName = os.path.join(outPath, fName)
    tempOutName = os.path.join(outPath, "TEMP_" + fName)
    outFile = codecs.open(tempOutName, 'w', encoding='utf8')
    for tweet in iterTweets(os.sep.join([sys.argv[1], fName])):
        timeInt = int(tweet[0])
        if tweet[2] != '302':
            time = str(timeInt)
            status = getStatus(time)
            title = clean(getTitle(time)).strip().replace('\t', ' ')
            if status or title:
                outFile.write(time + '\t\t' + clean(status) + '\t\t' + clean(getHashtag(time)) + '\t\t' + \
                               title + '\t\t' + json.dumps(entities(status)) + '\t\t' + json.dumps(entities(title)) + '\n')
    outFile.close()
    os.system("tac " + tempOutName + " > " + outName)
    os.remove(tempOutName)
