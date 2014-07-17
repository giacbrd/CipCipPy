"""Functions for several IO uses"""
from collections import namedtuple
import datetime, gzip, json, os

from . import replyRE, hashtagRE, months
from ..retrieval import getStoredValue




Tweet = namedtuple("Tweet", "id user http date status hashtags replies")
Query = namedtuple("Query", "number topic date tweettime newesttime")
Qrels = namedtuple("Qrels", "rel notrel")

def dataset_iter(path, start_time, end_time, reverse=False):
    dir_list = os.listdir(path)
    if reverse:
        dir_list.reverse()
    for fname in dir_list:
        curr_start, curr_end = [int(t) for t in fname.split("-")]
        if curr_start <= start_time <= curr_end or curr_start <= end_time <= curr_end:
            with gzip.open(filename=os.path.join(path, fname), mode='r') as gzip_file:
                lines = gzip_file
                if reverse:
                    lines = gzip_file.readlines()
                    lines.reverse()
                for line in lines:
                    tweet = json.loads(line.strip())
                    if start_time <= tweet[0] <= end_time:
                        yield tweet


def writeResults(results, runName, resultsPath, indexForPrint = None, numOfResults = float("inf")):
    """Write results text in TREC format
    queryIds - list of query numbers relative to results list
    indexForPrint - index object to retrieve tweets to print in the results, if false no tweets are printed"""
#    for r in results:
 #       if len(r) < 30:
  #          return
    f = open(os.path.join(resultsPath, runName), 'w')
    searcher = None
    try:
        if indexForPrint:
            searcher = indexForPrint.searcher()
        for q, r in results.iteritems():
            if r:
                #r = r.items()
                #r.sort(key = operator.itemgetter(1), reverse = True)
                num = min(numOfResults, len(r))
                for n in xrange(num):
                    tweet = '\n'
                    if indexForPrint:
                        #print r[n][0], searcher.document(id = unicode(r[n][0]))
                        tweet = '\t' + getStoredValue(searcher, r[n][0], 'status') + '\n'
                    f.write((q + '\t' + r[n][0] + '\t' + str(r[n][1]) + '\t' + runName + tweet).encode('ascii', 'replace'))
    finally:
        if indexForPrint:
            searcher.close()

def readQueries(filePath):
    """Returns tuples of query string and date from a topics file:
    (number, query topic, query date, query date as tweet id [, query date as tweet id of the most recent tweet])"""
    queries = []
    f = open(filePath)
    topics = f.read().split('\n</top>\n\n<top>\n')
    topics[0] = topics[0][6:]
    topics[-1] = topics[-1][:-6]
    for topic in topics:
        query = []
        i = topic.find(': ') + 2
        query.append(topic[i : i + 5])
        e = topic.find('<title>', i)
        if e == -1:
            i = topic.find('<query>', i) + len('<query>')
            j = topic.find('</query>', i)
        else:
            i = e + len('<title>')
            j = topic.find('</title>', i)
        query.append(unicode(topic[i:j].strip(), encoding='utf8'))
        i = topic.find('<querytime>', j) + len('<querytime>')
        j = topic.find('</querytime>', i)
        dateString = topic[i:j].strip()
        date = dateString.split(' ')
        time =  date[3].split(':')
        query.append(datetime.datetime(int(date[5]), months[date[1]], int(date[2]), int(time[0]), int(time[1]), int(time[2])))
        i = topic.find('<querytweettime>', j) + len('<querytweettime>')
        j = topic.find('</querytweettime>', i)
        query.append(int(topic[i:j].strip()))
        e = topic.find('<querynewesttweet>', j)
        if e != -1:
            i = e + len('<querynewesttweet>')
            j = topic.find('</querynewesttweet>', i)
            query.append(int(topic[i:j].strip()))
        queries.append(Query(*query))
    return queries

def readQrels(filePath, queryNumbers = None):
    """Return a map of queries and a set of relevant and a set of non-relevant tweet ids.
    queryNumbers is an iterator of query numbers in the TREC topics file format."""
    queryNumbersSet = None
    if queryNumbers:
        queryNumbersSet = set(int(qNum[2:]) for qNum in queryNumbers)
    queries = {}
    for line in open(filePath):
        l = line.strip().split(' ')
        q = int(l[0])
        if queryNumbers and q not in queryNumbersSet:
            continue
        if q not in queries:
            queries[q] = Qrels(set(), set())
        if int(l[3]) > 0:
            queries[q][0].add(l[2])
        else:
            queries[q][1].add(l[2])
    return queries


def iterTweets(filePath, skipNull = True):
    """Iterator over tweets in the plain text file filePath."""
    file = open(filePath) if filePath[-2:] != 'gz' else gzip.open(filePath)
    for line in file:
        try:
            line = unicode(line, encoding = 'utf8')
        except UnicodeDecodeError:
            print 'unicode error: ' + line
            continue
        try:
            l = tweetParser(line)
        except ValueError:
            continue
        if skipNull and (l[3] == 'null' or len(l) <= 4):
            continue
        else:
            yield l
    file.close()

def tweetParser(line):
    """Return a tuple or None if the tweet is null:
        (tweet id, user, http status, date object, status, tuple of hashtags, tuple of replied users)"""
    l = line.strip().split('\t')
    if len(l) < 5:
        raise ValueError("Incorrect line format of the corpus:  " + line)
    if l[3] != 'null':
        if len(l) > 5:
            l[4] = '\t'.join(l[4:])
            del l[5:]
        date = l[3].split(' ')
        time =  date[3].split(':')
        l[3] = datetime.datetime(int(date[5]), months[date[1]], int(date[2]), int(time[0]), int(time[1]), int(time[2]))
        if len(l) > 4:
            l.append(tuple(hashtagRE.findall(l[4])))
            l.append(tuple(replyRE.findall(l[4])))
    return Tweet(*l)

def dateFromFileName(fileName):
    """Return the datetime of a collection file name."""
    y, m, d = fileName[:4], fileName[4:6], fileName[6:8]
    return datetime.datetime(int(y), int(m), int(d))

def topicsFileName(filePath):
    """Returns the unique name of the set of topics (queries) defined in the filePath."""
    fileName = os.path.split(filePath)[1]
    if fileName[-3:].lower() == "txt":
        return fileName[:-4]
    else:
        return fileName
