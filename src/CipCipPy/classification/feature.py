"""Methods for extracting features (list of strings) from a text string."""
from inspect import isfunction
import json
import nltk, math, operator

from ..utils.hashtag import Segmenter
from ..utils import hashReplRE, urlRE, stopwords, punctuations, hashtagRE, replyRE, wordDotsRE


ANNOTATION_PREFIX = 'NMIS__aNn__'
URL_FEATURE = 'NMIS__UrL__'
HASHTAG_FEATURE = 'NMIS__Hashtag__'
MENTION_FEATURE = 'NMIS__Mention__'
ANNOTATION_EXPANSION_PREFIX = 'NMIS__aNnEXP__'
STEM_PREFIX = 'NMIS__Stem__'

class FeatureExtractor:
    """Concatenate feature extraction functions"""

    def __init__(self, functions):
        self.functions = functions

    def get(self, text):
        result = []
        for f in self.functions:
            if isfunction(f):
                result.extend(f(text))
        return result


filterSet = stopwords #| punctuations

punctuations2 = set(('\'', '"', '`')) | punctuations

#FIXME optimize singleton generators, redundant code
segmenter = None
def getSegmenter(dictionary):
    global segmenter
    if not segmenter:
        segmenter = Segmenter(dictionary)
    return segmenter

stemmer = None
def getStemmer():
    global stemmer
    if not stemmer:
        stemmer = nltk.stem.PorterStemmer()
    return stemmer

lemmatizer = None
def getLemmatizer():
    global lemmatizer
    if not lemmatizer:
        lemmatizer = nltk.stem.WordNetLemmatizer()
    return lemmatizer

def entityExpansion(data, min_linkprob, count):
    spots = data[0]
    mentions = data[1]
    result = []
    for spot in (s for s in spots if s["linkProbability"] >= min_linkprob):
        for entity in spot["candidates"]:
            ent_id = str(entity["entity"])
            ent_comm = entity["commonness"]
            curr_mentions = []
            for mention in (m for m in mentions[ent_id] if m["linkProbability"] >= min_linkprob):
                mention_name = mention["mention"]
                curr_mentions.append((mention_name, mention["linkProbability"] * ent_comm * mention["linkFrequency"]))
            curr_mentions = [m for m in curr_mentions if m[1] > 1.]
            curr_mentions.sort(key=operator.itemgetter(1), reverse=True)
            result.extend(curr_mentions[:count])
    if not result:
        return result
    result.sort(key=operator.itemgetter(1), reverse=True)
    #print text, mentions[:30]
    return [ANNOTATION_EXPANSION_PREFIX + m.replace(" ", "_") for m in zip(*result)[0]]


def terms(text):
    """Returns the unique, filtered, terms of a text"""
    terms = []
    text = hashReplRE.sub(" ", text)
    text = urlRE.sub(" ", text)
    text = wordDotsRE.sub(".", text)
    for sent in nltk.sent_tokenize(text):
        for subSent in sent.split(';'):
            terms.extend(nltk.word_tokenize(subSent))
    terms = [t.lower() for t in terms if t.strip() and len(t) > 1 and t != u'\ufffd']
    return [t for t in terms if t not in filterSet and not set(t).issubset(punctuations2)]

def lemmas(text):
    text_terms = terms(text)
    return [getLemmatizer().lemmatize(t) for t in text_terms]

def stems(text):
    text_terms = terms(text)
    return [STEM_PREFIX + getStemmer().stem(t) for t in text_terms]

def bigrams(text):
    """Returns term pairs of a text"""
    bigrams = []
    text = hashReplRE.sub(";", text)
    text = urlRE.sub(";", text)
    for sent in nltk.sent_tokenize(text):
        for subSent in sent.split(';'):
            bigrams.extend(nltk.bigrams(nltk.word_tokenize(subSent)))
    bigrams = [' '.join(b) for b in bigrams if u'\ufffd' not in b]
    return [b.lower().replace(' ', '_') for b in bigrams if not len(set(b) & punctuations2)]

def hashtags(text):
    """Returns hashtags of a text"""
    return [h for h in hashtagRE.findall(text)]

def mentions(text):
    """Returns mentioned users of a text"""
    return [r for r in replyRE.findall(text)]

def hasHashtags(text):
    """Returns hashtags of a text"""
    return [HASHTAG_FEATURE]if hashtagRE.findall(text) else []

def hasMentions(text):
    """Returns mentioned users of a text"""
    return [MENTION_FEATURE] if replyRE.findall(text) else []

def hasUrl(text):
    """Return a feature if there is a url in the text"""
    return [URL_FEATURE] if urlRE.findall(text) else []

def segmHashtags(text, dictionary):
    """Returns terms of the segmented hashtags of a text"""
    segmenter = getSegmenter(dictionary)
    return terms(' '.join(' '.join(segmenter.get(ht)[0]) for ht in hashtags(text)))

def segmHashtagsBigrams(text, dictionary):
    """Returns term pairs of the segmented hashtags of a text"""
    segmenter = getSegmenter(dictionary)
    hashBigr = []
    for ht in hashtags(text):
        hashBigr.extend(bigrams(' '.join(segmenter.get(ht)[0])))
    return hashBigr

def countAggregateAllEntities(nerTweet):
    """Returns a feature representing the count of the named entities"""
    result=[]
    count=nerTweet.count('/B-')
    for i in range(count):
        result.append('_ner_')
    return result

def countAggregateMostCommonEntities(nerTweet):
    """Returns a feature representing the count of the most common named entities"""
    entitiesName=['person','geo-loc','company']
    result=[]
    for ent in entitiesName:
        count=nerTweet.count('/B-'+ent)
        for i in range(count):
            result.append('_ner_')
    return result

def countSpecificAllEntities(nerTweet):
    """Returns a feature representing the count of each type of named entity"""
    entitiesName=['person','geo-loc','company','facility','product','band','sportsteam','movie','tv-show','other','NONE']
    result=[]
    for ent in entitiesName:
        count=nerTweet.count('/B-'+ent)
        for i in range(count):
            result.append('_'+ent+'_')
    return result

def countSpecificMostCommonEntities(nerTweet):
    """Returns a feature representing the count of each type of the most common named entities"""
    entitiesName=['person','geo-loc','company']
    result=[]
    for ent in entitiesName:
        count=nerTweet.count('/B-'+ent)
        for i in range(count):
            result.append('_'+ent+'_')
    return result

def countIntersectingTerms(text, query):
    """Returns a feature representing the number of terms in common between two texts"""
    result=[]
    termsQuery=terms(query)
    termsText=terms(text)
    intersectionNumber = len(set(termsQuery) & set(termsText))
    normalizedIntersection=math.floor((float(intersectionNumber)/float(len(termsQuery)))*5.0)
    for i in range(int(normalizedIntersection)):
        result.append('_intersect_')
    return result

def annotations(annotationTweet):
    return [ANNOTATION_PREFIX + a for a in annotationTweet.split('\t')]

