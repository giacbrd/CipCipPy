"""Methods for extracting features (list of strings) from a text string."""
from ..utils.hashtag import Segmenter
from ..utils import hashReplRE, urlRE, stopwords, punctuations, hashtagRE, replyRE
import nltk, math

ANNOTATION_PREFIX = 'NMIS__aNn__'
URL_FEATURE = 'NMIS__UrL__'

class FeatureExtractor:
    """Concatenate feature extraction functions"""

    def __init__(self, functions):
        self.functions = functions

    def get(self, text):
        result = []
        for f in self.functions:
            result.extend(f(text))
        return result

filterSet = stopwords | punctuations

punctuations2 = set(('\'', '"', '`'))

segmenter = None
def getSegmenter(dictionary):
    global segmenter
    if not segmenter:
        segmenter = Segmenter(dictionary)
    return segmenter

def terms(text):
    """Returns the unique, filtered, terms of a text"""
    terms = []
    text = hashReplRE.sub(" ", text)
    text = urlRE.sub(" ", text)
    for sent in nltk.sent_tokenize(text):
        for subSent in sent.split(';'):
            terms.extend(nltk.word_tokenize(subSent))
    terms = [t.lower() for t in terms if t.strip() and len(t) > 1 and t != u'\ufffd']
    return [t for t in terms if t not in filterSet and not len(set(t) & punctuations2)]

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

