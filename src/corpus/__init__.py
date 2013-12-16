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

Corpus builders to generate new datasets from the original TREC corpus.
Filter classes have a filter method which takes a corpus line (a tweet), and returns the new line or None if the tweet has to be filtered out.
"""

__version__ = "0.1"
__authors__ = ["Giacomo Berardi <giacomo.berardi@isti.cnr.it>",
               "Andrea Esuli <andrea.esuli@isti.cnr.it>",
               "Diego Marcheggiani <diego.marcheggiani@isti.cnr.it>"]

import os, shutil
from filters import BaseFilter
import httplib2
from ..utils.fileManager import tweetParser, iterTweets
import re
from HTMLParser import HTMLParser

def build(filters, inPath, outPath):
    """filters is an iterator over objects for filtering, for each line they are applied in the iterator order."""
    filters = [BaseFilter()] + list(filters)
    if not os.path.exists(outPath):
        os.makedirs(outPath)
    dirList = os.listdir(inPath)
    for fName in dirList:
        outFile = open(os.sep.join([outPath, fName]), 'w')
        for line in open(os.sep.join([inPath, fName])):
            line = line.strip()
            for filter in filters:
                line = filter.filter(line)
                if line == None:
                    break
            if line != None:
                outFile.write(line + '\n')
        outFile.close()

def fuse(inPaths, filters, outPath, separator = '\t\t'):
    """Fuse several corpus in one, appending the different contents of tweets with the same id,
    divided by separator"""
    pass

def enrich(corpusPath1, corpusPath2, filters, outPath):
    """Create a corpus that contains the tweets of corpus1,
    and the tweets of corpus2 those are not in corpus1
    Filters are applied to corpus2"""
    filters = [BaseFilter()] + list(filters)
    if not os.path.exists(outPath):
        os.makedirs(outPath)
    dirList1 = os.listdir(corpusPath1)
    dirList2 = os.listdir(corpusPath2)
    for fName in dirList2:
        if fName not in dirList1:
            shutil.copy(os.sep.join([corpusPath2, fName]), os.sep.join([outPath, fName]))
            continue
        outFile = open(os.sep.join([outPath, fName]), 'w')
        iter1 = open(os.sep.join([corpusPath1, fName]))
        iter2 = open(os.sep.join([corpusPath2, fName]))
        line1 = iter1.next()
        line2 = iter2.next()
        tweet1 = line1.strip().split('\t')
        tweet2 = line2.strip().split('\t')
        time1 = int(tweet1[0])
        time2 = int(tweet2[0])
        while True:
            if time1 == time2:
                outFile.write(line1 + '\n')
                line1 = iter1.next()
                line2 = iter2.next()
                tweet1 = line1.strip().split('\t')
                tweet2 = line2.strip().split('\t')
                time1 = int(tweet1[0])
                time2 = int(tweet2[0])
                continue
            if time2 > time1:
                outFile.write(line1 + '\n')
                line1 = iter1.next()
                tweet1 = line1.strip().split('\t')
                time1 = int(tweet1[0])
                continue
            if time1 > time2:
                for filter in filters:
                    line2 = filter.filter(line2)
                    if line2 == None:
                        break
                    if line2 != None:
                        outFile.write(line2 + '\n')
                line2 = iter2.next()
                tweet2 = line2.strip().split('\t')
                time2 = int(tweet2[0])
                continue



_tweetBegin = "<span class=\"entry-content\">"
_tweetEnd = "<span class=\"meta entry-meta\""
_timestampRE = re.compile("<span class=\"published timestamp\" data=\"\\{time:'([^']+)'\\}\">")
_htmlParser = HTMLParser()

def parseHtml(page):
    """Return a tweet timestamp and status from the tweet html page, 'null' strings if errors in the page."""
    timestamp = 'null'
    status = 'null'
    i = page.find(_tweetBegin)
    j = page.find(_tweetEnd)
    if i != -1 and j != -1:
        status = page[i:j]
        status = _htmlParser.unescape(re.sub(r"[\t]", "", re.sub(r"[\n\r]", "", re.sub(r"<(.|\n)*?>", "", status))).strip())
    timestampMatch = _timestampRE.search(page)
    if timestampMatch != None:
        timestamp = timestampMatch.group(1)
    return timestamp, status

# TODO verify already downloaded tweets
def download(datPath, outPath, corpusPath = None, newIdsPath = None):
    """Download html pages of tweets and create a corpus in outPath, download only not already retrieved tweets of corpusPath if it is a corpus directory of plain text files."""
    def retrieve(url):
        try:
            content = http.request(url)
        except httplib2.HttpLib2Error as e:
            print 'error:', url, e
        return content[0]['status'], content[1]
    badHttpStatus = frozenset(('403', '404'))
    http = httplib2.Http()
    if newIdsPath != None:
        newIdsFile = open(newIdsPath)
    for names in os.walk(datPath):
        for fName in names[2]:
            if fName[-3:] == 'dat':
                outFile = open(os.path.join(outPath, fName[:-4] + ".html.txt"), 'w')
                datFile = open(os.path.join(names[0], fName))
                corpusFileLines = open(os.path.join(corpusPath, fName[:-4] + ".html.txt")).readlines() if corpusPath != None else []
                i = 0
                for line in datFile:
                    tweetLine = ''
                    line = line.strip().split('\t')
                    url = "http://twitter.com/" + line[1] + "/status/" + line[0]
                    if newIdsPath != None:
                        newIdLine = newIdsFile.next().strip().split(' ')
                        assert(newIdLine[0] == line[0])
                        if newIdLine[1] in badHttpStatus:
                            tweetLine = line[0] + '\t' + line[1] + '\t' + newIdLine[1] + '\tnull\tnull\n'
                    if not tweetLine:
                        if corpusPath != None:
                            tweet = tweetParser(corpusFileLines[i])
                            if tweet[3] != 'null':
                                i += 1
                                continue
                            assert(tweet[0] == line[0])
                        httpStatus, page = retrieve(url)
                        timestamp, status = parseHtml(page)
                        tweetLine = line[0] + '\t' + line[1] + '\t' + httpStatus + '\t' + timestamp + '\t' + status + '\n'
                    if corpusPath != None:
                        corpusFileLines[i] = tweetLine
                        i += 1
                    else:
                        corpusFileLines.append(tweetLine)
                for line in corpusFileLines:
                    outFile.write(line)

