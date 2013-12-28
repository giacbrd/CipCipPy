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

Real-time filtering package.
"""

__version__ = "0.1"
__authors__ = ["Giacomo Berardi <giacomo.berardi@isti.cnr.it>",
               "Andrea Esuli <andrea.esuli@isti.cnr.it>",
               "Diego Marcheggiani <diego.marcheggiani@isti.cnr.it>"]


from ..classification.feature import *
import cPickle
from ..classification.scikitClassifiers import TrainingSet, NBClassifier, SVMClassifier
import os

_extractorStatus = FeatureExtractor((terms, bigrams, hashtags, mentions, hasUrl))
_extractor1 = FeatureExtractor((terms, bigrams))



class Filterer:

    def featureExtract(self, text, external = True):
        """Extracts all the features from an sample of text"""
        features = []
        text = text.split('\t\t')
        if text[0]: # status
            features.extend(_extractorStatus.get(text[0]))
        if text[1]: # hashtag
            features.extend(_extractor1.get(text[1]))
        if external and text[2]: # link title
            features.extend(_extractor1.get(text[2]))
        if external and text[3]: # annotations
            features.extend(annotations(text[3]))
        return features

    def featureExtractQuery(self, text, external = True):
        """Extracts all the features from a query"""
        features = []
        text = text.split('\t\t')
        if text[0]: # topic
            features.extend(_extractor1.get(text[0]))
        if external and text[1]: # annotations
            features.extend(annotations(text[1]))
        return features

    def cleanUtf(self, features):
        """Remove badly encoded terms."""
        cleanedFeatures = []
        for feat in features:
            feat = feat.encode('ascii', 'replace')
            if feat:
                cleanedFeatures.append(feat)
        return cleanedFeatures

    def intersect(self, query, text):
        """How many terms query amd text have in common."""
        return len(set(terms(query)) & set(terms(text)))

class SupervisedFilterer(Filterer):

    def __init__(self, classifier):
        self.classifier = classifier

    def cutOnLinkProb(self, features, linkProb):
        result = []
        for f in features:
            ff = f.split(' ')
            if f.startswith(ANNOTATION_PREFIX) and len(ff) == 4:
                try:
                    fl = float(ff[2])
                except ValueError:
                    fl = 0.
                if fl > linkProb:
                    result.append(ff[0])
            else:
                result.append(f)
        return result

    def get(self, queries, queriesAnnotated, neg, trainingSetPath, filteringIdsPath,
            qrels, external, minLinkProb, annotationFilter = False, dumpsPath = None):
        """ Return filtered tweets for query topics and the relative time ranges.
        queries - queries from a topic file
        queriesAnnotated - queries from a topic file with annotated topics
        neg - number of negative samples
        trainingSetPath - training set dir
        filteringIdsPath - path of ids and content per query (test set) for realtime filtering.
                           The tweet line format is defined in the method featureExtract
        qrels - relevance judgements
        external - True for using external information, otherwise False
        minLinkProb - minimum link probability for an annotation to be selected as feature
        annotationFilter - If True a tweet is passed through supervised learning only if
        the intersection of annotation with the query or the first tweet is not empty
        dumpsPath - path where to store serialized results
        """
        results = {}
        for i, q in enumerate(queries):
            if int(q[0][2:]) not in qrels:
                continue
            print q
            results[q[0]] = []
            # (positives, negatives) ordered by relevance
            # ((tweetId, [features..]), (tweetId, [features..]), ..], [(tweetId, [features..]), ...])
            training = cPickle.load(open(os.path.join(trainingSetPath, q[0])))
            rawTweets=[]
            testFile = open(os.path.join(filteringIdsPath, q[0]))
            posAnnotations = set()
            # add the query as positive example
            features = self.featureExtractQuery(q[1] + '\t\t' + queriesAnnotated[i][1], external)
            features = self.cutOnLinkProb(features, minLinkProb)
            posAnnotations.update((feat for feat in features if feat.startswith(ANNOTATION_PREFIX)))
            rawTweets.append((q[0], True, features))
            # add the first tweet as positive example
            for line in testFile:
                tweetId, null, text = unicode(line, encoding='utf8').partition('\t\t')
                results[q[0]].append((tweetId, '1.0\tyes'))
                features = self.featureExtract(text[:-1], external)
                features = self.cutOnLinkProb(features, minLinkProb)
                posAnnotations.update((feat for feat in features if feat.startswith(ANNOTATION_PREFIX)))
                rawTweets.append((tweetId, True, features))
                break
            for tweetId, features in training[1][:neg]:
                features = self.cutOnLinkProb(features, minLinkProb)
                rawTweets.append((tweetId, False, features))
            classifier = None
            training = TrainingSet(rawTweets, 0)
            if rawTweets:
                training.countVectorize()
                self.classifier.retrain(training.vectoridf, training.tweetTarget)
            #for e, v in enumerate(training.vectoridf[:2]):
            #    fe = training.features[e].split(' ')
            #    col = v.nonzero()[1]
            #    for z in xrange(len(fe)):
            #        print fe[z], v[0,col[z]]
            #    print training.tweetTarget[e]
            # do not train the first tweet
            for line in testFile:
                tweetId, null, text = unicode(line, encoding='utf8').partition('\t\t')
                features = self.featureExtract(text[:-1], external)
                features = self.cutOnLinkProb(features, minLinkProb)
                if not features:
                    continue
                if annotationFilter:
                    testAnnotation = set(feat for feat in features if feat.startswith(ANNOTATION_PREFIX))
                    if not posAnnotations.intersection(testAnnotation):
                        continue
                #nb.test(tweetId, features)
                test=training.vectorizeTest((tweetId,False,features))
                classification = self.classifier.classify(test)
                #print tweetId, features, 'C' + str(classification)
                #print classifier.getProb(test)
                if classification == 1:
                    score = self.classifier.getProb(test) if callable(getattr(self.classifier, "getProb", None)) else 1.
                    results[q[0]].append((tweetId, str(score) + '\tyes'))
                    if tweetId in qrels[int(q[0][2:])][0]:
                        training.addExample((tweetId, True, features))
                        if annotationFilter:
                            posAnnotations.update((feat for feat in features if feat.startswith(ANNOTATION_PREFIX)))
                        # TODO pop a old positive sample? only if rules are not used?
                    else:
                        training.addExample((tweetId, False, features))
                    training.countVectorize()
                    self.classifier.retrain(training.vectoridf, training.tweetTarget)
            testFile.close()
            if dumpsPath:
                cPickle.dump(results[q[0]], open(os.path.join(dumpsPath, q[0]), 'w'))
        return results


@DeprecationWarning
class NBFilterer(Filterer):

    def featureExtract(self, text, query, external = True):
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
        if query:
            features.extend(countIntersectingTerms(';'.join(text), query))
        return features

    def get(self, queries, n, m, rulesCount, trainingSetPath, filteringIdsPath, qrels, external, dumpsPath = None):
        """ Return filtered tweets for query topics and the relative time ranges.
        queries - queries from a topic file
        n - number of positive samples
        m - number of negative samples
        rulesCount - number of positive samples to find before starting classification
        trainingSetPath - training set dir
        filteringIdsPath - path of ids and content per query (test set) for realtime filtering
        qrels - relevance judgements
        external - True for using external information, otherwise False
        dumpsPath - path where to store serialized results
        """
        results = {}
        for q in queries:
            currRulesCount = rulesCount if rulesCount > 0 else 0
            print currRulesCount, n, m, q
            results[q[0]] = []
            # (positives, negatives) ordered by relevance
            # ((tweetId, [features..]), (tweetId, [features..]), ..], [(tweetId, [features..]), ...])
            training = cPickle.load(open(os.path.join(trainingSetPath, q[0])))
            rawTweets=[]
            # FIXME justify using reversed
            # FIXME the query should be a positive sample in the training
            for tweetId, features in reversed(training[0][:n]):
                rawTweets.append((tweetId, True, self.cleanUtf(features)))
            for tweetId, features in training[1][:m]:
                rawTweets.append((tweetId, False, self.cleanUtf(features)))
            classifier = None
            training = TrainingSet(rawTweets, n)
            if rawTweets:
                training.countVectorize()
                classifier=NBClassifier(training.vectorcounts, training.tweetTarget)
            # do not train the first tweet
            firstTweet = True
            for line in open(os.path.join(filteringIdsPath, q[0])):
                tweetId, null, text = line.partition('\t\t')
                if currRulesCount > 0:
                    if self.intersect(q[1], text):
                        results[q[0]].append((tweetId, '0.5\tyes'))
                        if firstTweet:
                            firstTweet = False
                            continue
                        features = self.cleanUtf(self.featureExtract(text[:-1], q[1], external))
                        if tweetId in qrels[int(q[0][2:])][0]:
                            training.addExample((tweetId, True, features))
                            currRulesCount -= 1
                        else:
                            training.addExample((tweetId, False, features))
                    continue
                elif currRulesCount == 0:
                    if not training.features:
                        raise Exception("No training set for classification")
                    training.countVectorize()
                    if classifier:
                        classifier.retrain(training.vectorcounts, training.tweetTarget)
                    else:
                        classifier=NBClassifier(training.vectorcounts, training.tweetTarget)
                    currRulesCount = -1
                features = self.cleanUtf(self.featureExtract(text[:-1], q[1], external))
                if not features:
                    continue
                #nb.test(tweetId, features)
                test=training.vectorizeTest((tweetId,False,features))
                classification = classifier.classify(test)
                #print tweetId, features, 'C' + str(classification[0])
                #print classifier.getProb(test)
                if classification == 1:
                    results[q[0]].append((tweetId, str(classifier.getProb(test)) + '\tyes'))
                    if firstTweet:
                        firstTweet = False
                        continue
                    if tweetId in qrels[int(q[0][2:])][0]:
                        training.addExample((tweetId, True, features))
                        # TODO pop a old positive sample? only if rules are not used?
                    else:
                        training.addExample((tweetId, False, features))
                    training.countVectorize()
                    classifier.retrain(training.vectorcounts, training.tweetTarget)
            if dumpsPath:
                cPickle.dump(results[q[0]], open(os.path.join(dumpsPath, q[0]), 'w'))
        return results