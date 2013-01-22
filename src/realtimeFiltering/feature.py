from CipCipPy.classification.feature import *
#from CipCipPy.indexing import getIndexPath
#from CipCipPy.retrieval import getStoredValue
#import whoosh.index


#_extractor1 = FeatureExtractor((terms, bigrams, hashtags, segmHashtags, segmHashtagsBigrams))
#_extractor2 = FeatureExtractor((terms, bigrams))
#_queryFeatureExtractor = FeatureExtractor((terms, bigrams))
#_ruleFeatureExtractor = FeatureExtractor((terms,))
#
#_storedStatus = whoosh.index.open_dir(getIndexPath('storedStatus')).searcher()
#_storedHashtag = whoosh.index.open_dir(getIndexPath('storedHashtag')).searcher()
#_storedLinkTitle = whoosh.index.open_dir(getIndexPath('storedLinkTitle')).searcher()
#_storedNamedEntity = whoosh.index.open_dir(getIndexPath('storedNamedEntity')).searcher()
#
#def getStatus(indexId):
#    return getStoredValue(_storedStatus, indexId, 'status')
#def getTitle(indexId):
#    return getStoredValue(_storedLinkTitle, indexId, 'title')
#def getHashtag(indexId):
#    return getStoredValue(_storedHashtag, indexId, 'hashtags')
#def getNE(indexId):
#    return getStoredValue(_storedNamedEntity, indexId, 'namedEntities')
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
    features = []
    text = text.split('\t\t')
    if text[0]: # status
        features.extend(_extractor2.get(text[0]))
    if text[1]: # hashtag
        features.extend(_extractor2.get(text[1]))
    if external and text[2]: # named entity
        features.extend(countSpecificAllEntities(text[2]))
    if external and text[3]: # link title
        features.extend(_extractor2.get(text[3]))
    features.extend(countIntersectingTerms(';'.join(text), query))
    return features