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

Retrieval package.
"""

__version__ = "0.1"
__authors__ = ["Giacomo Berardi <giacomo.berardi@isti.cnr.it>",
               "Andrea Esuli <andrea.esuli@isti.cnr.it>",
               "Diego Marcheggiani <diego.marcheggiani@isti.cnr.it>"]

import sys
import traceback

import whoosh.index as index
from whoosh.qparser import QueryParser
import numpy
from whoosh.qparser import BoostPlugin

from ..utils import hashtag, stopwords
from ..indexing import getIndexPath
from ..utils.cache import *
from ..classification import feature


def getStoredValue(searcher, tweetId, valueKey):
    """return a stored value for an entry of the index"""
    result = searcher.document(id = unicode(tweetId))
    if result != None:
        return result[valueKey]
    else:
        return None


class Searcher:
    
    def __init__(self, statusIndexName, hashtagIndexName, linkTitlesIndexName, storedValuesIndexName, dictionary, overwrite = False):
        """Generate a searcher given the name of the indexes stored by CipCipPy"""
        self.statusIndexName = statusIndexName
        self.hashtagIndexName = hashtagIndexName
        self.linkTitlesIndexName = linkTitlesIndexName
        self.storedValues = index.open_dir(getIndexPath(storedValuesIndexName)).searcher()
        self.segmenter = hashtag.Segmenter(dictionary)
        self.results = None
        # FIXME can not delete everything: another process may be working on the cache
        if overwrite:
            try:
                cleanCache('retrieval.Searcher')
            except CacheException:
                pass

    def getExpansedQuery(self, query, resultsExpans, complementary = False):
        """Expand a query using some first retrieved results"""
        qp = QueryParser("status", schema = self.statusIndex.schema)
        qp.add_plugin(BoostPlugin())
        q = qp.parse('* NOT (' + ' OR '.join(t for t in query[1].split(' ') if t.strip()) + ')' if complementary else query[1])
        res = self.statusSearcher.search(q, limit = resultsExpans)
        if len(res):
            hashtagFreq = {}
            for r in res:
                for ht in self.getStoredValue(r['id'], 'hashtags').split(' '):
                    if ht != '':
                        for t in self.segmenter.get(ht)[0]:
                            if len(t) > 1 and t.lower() not in stopwords:
                                hashtagFreq[t] = hashtagFreq.get(t, 0.) + 1.
            if hashtagFreq: # create a query string with each hashtag term weighted by his frequency
                return ' OR '.join('(' + hq[0] + '^' + str(hq[1]) + ')' for hq in zip(hashtagFreq.keys(), list(numpy.array(hashtagFreq.values()) / numpy.linalg.norm(hashtagFreq.values(), ord=2))))
            else:
                return ''

    def getStoredValue(self, indexId, valueKey):
        """return a stored value for an entry of the index, that is not stored in the indexes for searching"""
        return getStoredValue(self.storedValues, indexId, valueKey)

    def get(self, queries, scoringObj, numOfResults, scoreWeights = (0.2, 0.2, 0.2, 0.2), resultsExpans = 20, threshold = 0., complementary = False):
        """Search a list of text queries and iterates on the results.
        queries - list of tuples of text queries and dates
        scoringObj - a whoosh object of a scoring class (for weighting results)
                scoreWeights - weights for each type of score
        resultsExpans - number of results to use for hashtag query expansion
        threshold - if the score value is lower than threshold, filter out the result
        complementary - retrieve results for the complementary query (documents not relevant to the query)
        """
        self.results = {}
        statusW, hashtagW, linkTitleW, dateW = scoreWeights
        try:
            for queryIndex, query in enumerate(queries):
                self.statusIndex = index.open_dir(getIndexPath(self.statusIndexName, query[3])) # index data path
                self.statusSearcher = self.statusIndex.searcher(weighting = scoringObj)
                self.hashtagSearcher, self.linkTitleSearcher = None, None
                if hashtagW:
                    self.hashtagIndex = index.open_dir(getIndexPath(self.hashtagIndexName, query[3])) # path of index of segmented hashtags
                    self.hashtagSearcher = self.hashtagIndex.searcher(weighting = scoringObj)
                if linkTitleW:
                    self.linkTitleIndex = index.open_dir(getIndexPath(self.linkTitlesIndexName, query[3])) # path of index of link titles
                    self.linkTitleSearcher = self.linkTitleIndex.searcher(weighting = scoringObj)
                dataId = self.statusIndexName + self.hashtagIndexName + self.linkTitlesIndexName + str(query)
                resultId = dataId + str(scoringObj) + str(numOfResults) + str(resultsExpans) + str(scoreWeights)
                result = getCache('retrieval.Searcher', resultId)
                if result == None:
                    cachedData = getCache('retrieval.Searcher', dataId + str(scoringObj) + str(numOfResults) + str(resultsExpans))
                    if cachedData != None:
                        res, scores, resHash, scoresHash, resLink, scoresLink, dateVect = cachedData
                    else:
                        query = list(query)
                        query[1] = ' '.join(feature.terms(query[1]))
                        ### HASHTAGS QUERY EXPANSION ###
                        expQuery = ''
                        if resultsExpans:
                            expQuery = self.getExpansedQuery(query, resultsExpans, complementary)
                        ### RETRIEVE FROM INDEXES ###
                        qp = QueryParser("status", schema = self.statusIndex.schema)
                        if complementary:
                            queryStatus = '* NOT (' + ' OR '.join(t for t in query[1].split(' ') if t.strip()) + ')'
                        else:
                            # disjunction of the cunjunctions of all the pairs of the query
                            queryStatus = [t for t in query[1].split(' ') if t.strip()]
                            queryStatus = frozenset(frozenset((t1, t2)) for t1 in queryStatus for t2 in queryStatus)
                            queryStatus = ' OR '.join(['(' + ' AND '.join(tuple(t)) + ')' for t in queryStatus])
                        q = qp.parse(queryStatus)
                        res = self.statusSearcher.search(q, limit=numOfResults)
                        if expQuery:
                            q = qp.parse(expQuery)
                            res2 = self.statusSearcher.search(q, limit=numOfResults)
                            res2.upgrade_and_extend(res)
                            res = res2
                        scores = numpy.array([float(r.score) for r in res])
                        scores /= numpy.linalg.norm(scores, ord=2)
                        res = [r.fields() for r in res]
                        resHash, scoresHash, resLink, scoresLink, dateVect = None, None, None, None, None
                        if hashtagW:
                            qpHash = QueryParser("hashtags", schema = self.hashtagIndex.schema)
                            q = qpHash.parse(queryStatus)
                            resHash = self.hashtagSearcher.search(q, limit=numOfResults)
                            if expQuery:
                                q = qpHash.parse(expQuery)
                                resHash2 = self.hashtagSearcher.search(q, limit=numOfResults)
                                resHash2.upgrade_and_extend(resHash)
                                resHash = resHash2
                            scoresHash = numpy.array([float(r.score) for r in resHash])
                            scoresHash /= numpy.linalg.norm(scoresHash, ord=2)
                            resHash = [r.fields() for r in resHash]
                        if linkTitleW:
                            qpLink = QueryParser("title", schema = self.linkTitleIndex.schema)
                            q = qpLink.parse(queryStatus)
                            resLink = self.linkTitleSearcher.search(q, limit=numOfResults)
                            if expQuery:
                                q = qpLink.parse(expQuery)
                                resLink2 = self.linkTitleSearcher.search(q, limit=numOfResults)
                                resLink2.upgrade_and_extend(resLink)
                                resLink = resLink2
                            scoresLink = numpy.array([float(r.score) for r in resLink])
                            scoresLink /= numpy.linalg.norm(scoresLink, ord=2)
                            resLink = [r.fields() for r in resLink]
                        if dateW:
                            dateVect = numpy.array([float(self.getStoredValue(r['id'], 'date').strftime('%Y%m%d%H%M%S')) for r in res])
                            dateVect -= min(dateVect)
                            dateVect /= numpy.linalg.norm(dateVect, ord=2)
                        storeCache('retrieval.Searcher', dataId + str(scoringObj) + str(numOfResults) + str(resultsExpans), (res, scores, resHash, scoresHash, resLink, scoresLink, dateVect))
                    ### COMBINE RESULTS ###
                    result = {}
                    for i, r in enumerate(res):
                        result[r['id']] = statusW * scores[i] + (dateW * dateVect[i] if dateW else 0.)
                    if hashtagW:
                        for i, r in enumerate(resHash):
                            if r['id'] in result:
                                result[r['id']] = result[r['id']] + hashtagW * scoresHash[i]
                    if linkTitleW:
                        for i, r in enumerate(resLink):
                            result[r['id']] = result.get(r['id'], 0.) + linkTitleW * scoresLink[i]
                    storeCache('retrieval.Searcher', resultId, result)
                # order by date and delete duplicates
                result = [(i, result[i]) for i in sorted(result.keys(), reverse=True)]
                alreadySeen = set()
                for i in reversed(xrange(len(result))):
                    tweetHash = int(hashlib.md5(self.getStoredValue(result[i][0], 'status').encode('ascii', 'ignore')).hexdigest()[:12], 16)
                    if result[i][1] < threshold or tweetHash in alreadySeen:
                        del result[i]
                    alreadySeen.add(tweetHash)
                self.results[query[0]] = result
        except Exception:
            print traceback.format_exc()
            sys.exit(1)
        finally:
            self.statusSearcher.close()
            if self.hashtagSearcher:
                self.hashtagSearcher.close()
            if self.linkTitleSearcher:
                self.linkTitleSearcher.close()
        return self.results

