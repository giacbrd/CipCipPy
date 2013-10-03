"""Functions for caching data"""

import hashlib
import os
import shutil
import cPickle
from ..config import CACHE_PATH

class CacheException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def getCache(path, idText):
    """Verify if there is cached data for the unique string that identifies 
    the data and return it, else return None."""
    fName = hashlib.md5(idText).hexdigest()
    cachePath = os.path.join(CACHE_PATH, path)
    if not os.path.exists(cachePath):
        os.makedirs(cachePath)
    cacheFilePath = os.path.join(cachePath, fName)
    if os.path.isfile(cacheFilePath):
        return cPickle.load(open(cacheFilePath))
    else:
        return None
    
def storeCache(path, idText, data, overwrite = False):
    """Store data in cache."""
    fName = hashlib.md5(idText).hexdigest()
    cachePath = os.path.join(CACHE_PATH, path)
    if not os.path.exists(cachePath):
        os.makedirs(cachePath)
    cacheFilePath = os.path.join(cachePath, fName)
    if os.path.isfile(cacheFilePath) and not overwrite:
        raise CacheException("This data already exists in the cache!")
    else:
        cPickle.dump(data, open(cacheFilePath, 'w'))
        
def cleanCache(path = None, idText = None):
    """Delete cached data, if no argument is specified delete all the cache."""
    if idText == None:
        if path == None:
            shutil.rmtree(CACHE_PATH)
        elif os.path.isdir(os.path.join(CACHE_PATH, path)):
            shutil.rmtree(os.path.join(CACHE_PATH, path))
        else:
            raise CacheException("Cache path does not exist!")
    else:
        fName = hashlib.md5(idText).hexdigest()
        cacheFilePath = os.path.join(CACHE_PATH, path, fName)
        if os.path.isfile(cacheFilePath):
            os.remove(cacheFilePath)
        else:
            raise CacheException("Cached data does not exist!")