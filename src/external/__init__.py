#    CipCipPy - Twitter IR system for the TREC Microblog track.
#    Copyright (C) <2011-2013>  Giacomo Berardi, Andrea Esuli, Diego Marcheggiani
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
CipCipPy

Retrievers and interfaces of external resources.
"""

__version__ = "0.1"
__authors__ = ["Giacomo Berardi <giacomo.berardi@isti.cnr.it>", 
               "Andrea Esuli <andrea.esuli@isti.cnr.it>", 
               "Diego Marcheggiani <diego.marcheggiani@isti.cnr.it>"]

import urllib2
import re
import time
import sys
import inspect
from ..utils.cache import *



htmlClean = re.compile("<.*?>")

userAgent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': userAgent,}

class News:
    """Manage content retrieved from Reuters for given topics."""
    
    def __init__(self, queries, numOfPages):
        """queries are used to retrieve the first numOfPages articles, for each, from Reuters"""
        
        self.queries = queries
        self.schema = ('mobile.reuters.com', '<p>', '<div class="lnk">')
        self.numOfPages = numOfPages
        
        cacheId = str(self.queries) + str(self.schema) + str(self.numOfPages)
        
        self.contents = getCache('external.News', cacheId)
        
        if self.contents == None:
            self.retrieve()
            storeCache('external.News', cacheId, self.contents)
        
    def getFeatureVectors(self, featureExtractor):
        """Create vector of features, according to the function featureExtractor, for each query, from the external content"""
        cacheId =  inspect.getSource(featureExtractor) + str((self.queries)) + str(self.schema) + str(self.numOfPages)      
        vectors = getCache('external.News.getFeatureVectors', cacheId)
        if vectors == None:
            vectors = [featureExtractor(p) for p in self.contents if p]
            storeCache('external.News.getFeatureVectors', cacheId, vectors)
        return vectors
    
    def getContents(self):
        return self.contents

    def retrieveContents(self):
        for query in self.queries:
            alreadySeen = set()
            n = 0
            content = ''
            while True:
                url = 'http://google.com/search?q=' + query[0].strip().replace(' ', '+') + '+site%3A' + schema[0] + '&num=50&language=en'
                print url
                req = urllib2.Request(url, None, headers)
                resultsPage = urllib2.urlopen(req)
                resultsPage = resultsPage.read()
                j = 0
                try:
                    while n < self.numOfPages:
                        i = resultsPage.find('http', resultsPage.find('<li class=g>', j))
                        j = resultsPage.find('" ', i)
                        url = resultsPage[i : j]
                        print n, url
                        if not url.strip():
                            raise ValueError
                        if url not in alreadySeen:
                            alreadySeen.add(url)
                            req = urllib2.Request(url, None, headers)
                            page = urllib2.urlopen(req)
                            page = page.read()
                            page = page[page.find(schema[1]) : page.find(schema[2])]
                            content += (htmlClean.sub(' ', page) + '\n')
                            n += 1
                except ValueError:
                    query[0] = query[0].strip().replace(' ', '+OR+')
                    continue
                self.contents.append(content)
                break
        return self.contents
