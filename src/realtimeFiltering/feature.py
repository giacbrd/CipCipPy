"""Functions for features extraction from text"""

from ..classification.feature import *
#from CipCipPy.indexing import getIndexPath
#from CipCipPy.retrieval import getStoredValue
#import whoosh.index


_extractor1 = FeatureExtractor((terms, bigrams))
queryFeatureExtractor = FeatureExtractor((terms, bigrams))
#_ruleFeatureExtractor = FeatureExtractor((terms,))
#
#
#def featureExtractId(tweetId, query, external = True):
#    features = []
#    text = []
#    text1 = getStatus(tweetId)
#    if text1 != None:
#        text.append(text1)
#        features.extend(_extractor1.get(text1))
#    text2 = getTitle(tweetId)
#    if external and text2 != None:
#        text.append(text2)
#        features.extend(_extractor2.get(text2))
#    text3 = getNE(tweetId)
#    if external and text3 != None:
#        text.append(text3)
#        features.extend(countSpecificAllEntities(text3))
#    features.extend(countIntersectingTerms(';'.join(text), query))
#    return features

def featureExtractText(text, query, external = True):
    """Extracts all the features from an sample of text + query"""
    features = []
    text = text.split('\t\t')
    if text[0]: # status
        features.extend(_extractor1.get(text[0]))
    if text[1]: # hashtag
        features.extend(_extractor1.get(text[1]))
    if external and text[2]: # named entity
        features.extend(countSpecificAllEntities(text[2]))
    if external and text[3]: # link title
        features.extend(_extractor1.get(text[3]))
    features.extend(countIntersectingTerms(';'.join(text), query))
    return features