"""Function for creating annoated entities index"""

import os
import shutil

from whoosh.fields import Schema, TEXT, ID, DATETIME
import whoosh.index

from ..config import MEM_SIZE, PROC_NUM
from ..utils.fileManager import iterTweets
from . import getIndexPath


def index(corpusPath, name, tweetTime = None, stored = False, overwrite = True):
    """Indexing of the annotated entities in the tweets."""
    
    dirList = os.listdir(corpusPath)
    
    schema = Schema(id = ID(stored = True, unique = True),
                    date = DATETIME,
                    annotations = TEXT(stored = stored)
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
                writer.add_document(id = tweet[0],
                                    date = tweet[3],
                                    annotations = tweet[4]
                                    )
    
    writer.commit()
