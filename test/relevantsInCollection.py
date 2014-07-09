__author__ = 'giacomo'

import sys
import os

from CipCipPy.utils.fileManager import readQueries, readQrels, iterTweets


queries = readQueries(sys.argv[1])
qrels = readQrels(sys.argv[2], set(q[0] for q in queries))
collectionPath = sys.argv[3]

dirList = os.listdir(collectionPath)

pos = dict(((k, 0) for k in qrels))

def clean(text):
    return text.encode('utf8', 'replace') if text != None else ''

for fName in dirList:
    for tweet in iterTweets(os.path.join(collectionPath, fName)):
        tweetId = tweet[0]
        for q in queries:
            qKey = int(q[0][2:])
            if qKey not in qrels:
                continue
            if tweetId in qrels[qKey][0]:
                if int(q[3]) == int(tweetId):
                    print q, 'FIRST', tweet
                print q[0], q[1], '>>>>>>' , clean(tweet[4])
                pos[qKey] += 1

for q in queries:
    qKey = int(q[0][2:])
    if qKey not in qrels:
        continue
    print q, pos[qKey], len(qrels[qKey][0])