"""Function for creating twitter statuses index"""

import os
import shutil

from whoosh.fields import Schema, TEXT, ID, DATETIME, NUMERIC, KEYWORD
import whoosh.index

from ..config import MEM_SIZE, PROC_NUM
from ..utils.fileManager import iterTweets
from . import getIndexPath


def index(corpusPath, name, tweetTime = None, stored = False, overwrite = True):#, featureExtractor):
    """Indexing of the status of tweets."""
    
    dirList = os.listdir(corpusPath)
    
    schema = Schema(id = ID(stored = True, unique = True),
                    user = ID,
                    http = NUMERIC, # http state
                    date = DATETIME(stored = stored), # tweet date
                    status = TEXT(stored = stored), # status text of the tweet #TODO use a proper analyzer
                    hashtags = KEYWORD(stored = stored) # list of hashtags in the status
                    #replies = KEYWORD, # list of user replies in the status, as users
                    #vector = STORED
                    #score = NUMERIC(stored = True), # static score for ranking
                    #retweets = NUMERIC(type = type(1.), stored = True) # number of retweets of this tweet
                    ## next fields to fill on a second indexer pass ##
                    #retweets = KEYWORD, # list of retweets in the status, as tweet ids
                    #retweeteds = KEYWORD # list of tweets which retweet this tweet, as tweet ids
                    )

    indexPath = getIndexPath(name, tweetTime)
    if not os.path.exists(indexPath):
        os.makedirs(indexPath)
    else:
        if not overwrite:
            return
        shutil.rmtree(indexPath)
        os.makedirs(indexPath)
    ix = whoosh.index.create_in(indexPath, schema)
    writer = ix.writer(procs = PROC_NUM, limitmb = MEM_SIZE)
    
    for fName in dirList:
        #if tweetTime and dateFromFileName(fName) > tweetTime:
        #    continue
        #print fName
        for tweet in iterTweets(os.path.join(corpusPath, fName)):
            if tweetTime and int(tweet[0]) > tweetTime:
                continue
            if tweet[2] != '302': #and not 'RT @' in tweet[4]: # FIXME retweet filtering
                #v = featureExtractor(tweet[4].encode('ascii', 'replace'))
                writer.add_document(id = tweet[0],
                                    user = tweet[1],
                                    http = int(tweet[2]),
                                    date = tweet[3],
                                    status = tweet[4],
                                    hashtags = u' '.join(tweet[5])
                                    #replies = u' '.join(tweet[6]),
                                    #vector = repr(v)
                                    )
    
    writer.commit()
