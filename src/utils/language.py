# CipCipPy
# Twitter IR system for the TREC Microblog track.
#
# Authors: Giacomo Berardi <giacomo.berardi@isti.cnr.it>
#          Andrea Esuli <andrea.esuli@isti.cnr.it>
#          Diego Marcheggiani <diego.marcheggiani@isti.cnr.it>
# URL: <http://tag.isti.cnr.it/cipcippy/>
# For license information, see LICENSE

"""
CipCipPy

Tools for language detection.
"""

__version__ = "0.1"
__authors__ = ["Giacomo Berardi <giacomo.berardi@isti.cnr.it>",
               "Andrea Esuli <andrea.esuli@isti.cnr.it>",
               "Diego Marcheggiani <diego.marcheggiani@isti.cnr.it>"]

import re
import operator
import os
import string

class Lang:

    # SU TWITTER LE COSE SONO DIFFERENTI, AD ESEMPIO # e @ 
    #cleaner = re.compile('(\(|\)|[0-9]|\?|\.|,|!|-)')
    cleanTable = string.maketrans(string.punctuation.replace("'", "") + string.digits, ' ' * (len(string.punctuation + string.digits) - 1))
    hashRepl = re.compile('[@|#]\S+')
    url = re.compile('http://\S+')

    def __init__(self, trainPath):
        self.languages = {}
        for names in os.walk(os.path.abspath(trainPath)):
            for fName in names[2]:
                self.languages[fName[:-6]] = [line[0:3] for line in open(names[0] + '/' + fName)]

    def create_trigrams(self, text):
        #text = ' ' + self.__class__.cleaner.sub(" ", text)
        text = self.__class__.hashRepl.sub(" ", text)
        text = self.__class__.url.sub(" ", text)
        text = ' ' + text.translate(self.__class__.cleanTable)
        length = len(text)
        freq = {}
        for i in xrange(length):
            trigram = text[i : i+3].lower()
            if len(trigram) == 2:
                trigram += ' '
            elif len(trigram) == 1:
                trigram += '  '
            if trigram in freq:
                freq[trigram] += 1
            else:
                freq[trigram] = 1
        freq = freq.items()
        freq.sort(key = operator.itemgetter(1), reverse = True)
        return [tg[0] for tg in freq if tg[0].strip()]

    def calc_distance(self, distr, lang = 'english'):
        distance = 0
        for i in xrange(len(distr)):
            for j in xrange(len(self.languages[lang])):
                if self.languages[lang][j] == distr[i]:
                    break
                distance += abs(i - j)
        return distance

    def guess(self, text):
        if not text.strip():
            return None
        text = self.create_trigrams(text)
        currMin = float('inf')
        currLang = None
        for lang in self.languages.iterkeys():
            guessed = self.calc_distance(text, lang)
            #print lang, '\t', guessed
            if guessed < currMin:
                currMin = guessed
                currLang = lang
        return currLang

        

