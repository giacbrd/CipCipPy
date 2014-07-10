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

import cPickle
import os
import time

from ..classification.feature import *
from ..classification.scikitClassifiers import TrainingSet
from ..utils import retweetRE, textHash


class Filterer:

    def setFeatureExtractor(self, statusFeatEx, genericFeatEx, binaryFeatEx, minLinkProb, expansion_count = 0):
        self.statusFeatEx = FeatureExtractor(statusFeatEx)
        self.genericFeatEx = FeatureExtractor(genericFeatEx)
        self.binaryFeatEx = FeatureExtractor(binaryFeatEx)
        self.expansion_count = expansion_count
        self.minLinkProb = minLinkProb

    def featureExtract(self, text, external=True):
        """Extracts all the features from a sample"""
        features = []
        text = text.split('\t\t')
        if text[0]:  # status
            features.extend(self.statusFeatEx.get(text[0]))
        if text[1]:  # segmented hashtag
            features.extend(self.genericFeatEx.get(text[1]))
        if external and text[2]:  # link title
            features.extend(self.genericFeatEx.get(text[2]))
        if external and text[3]:  # status annotaions
            features.extend(entityExpansion(text[3], self.minLinkProb, self.expansion_count))
        if external and text[4]:  # link title annotation
            features.extend(entityExpansion(text[4], self.minLinkProb, self.expansion_count))
        return features

    def featureExtractBinary(self, text, external=True):
        """Extracts all the binary features from a sample"""
        binary_features = []
        text = text.split('\t\t')
        if text[0]:  # status
            binary_features.extend(self.binaryFeatEx.get(text[0]))
        #if external and text[3]:  # annotations
        #    binary_features.extend(annotations(text[3]))
        return binary_features

    def featureExtractQuery(self, text, external=True):
        """Extracts all the features from a query"""
        features = []
        text = text.split('\t\t')
        if text[0]:  # topic
            features.extend(self.genericFeatEx.get(text[0]))
        if external and text[1]:  # annotations
            features.extend(entityExpansion(text[1], self.minLinkProb, self.expansion_count))
        return features

    def featureExtractQueryBinary(self, text, external=True):
        """Extracts all the binary features from the query"""
        binary_features = []
        text = text.split('\t\t')
        #if external and text[1]:  # annotations
        #    binary_features.extend(annotations(text[1]))
        return binary_features

    def intersect(self, query, text):
        """How many terms query amd text have in common."""
        return len(set(terms(query)) & set(terms(text)))

    def tweetHash(self, tweet):
        return textHash(tweet.partition('\t\t')[0])


class SupervisedFilterer(Filterer):

    def __init__(self, classifier):
        self.classifier = classifier

    def get_annotations(self, features):
        """Returns the tuple of annotations in a list of features"""
        return (feat for feat in features if feat.startswith(ANNOTATION_PREFIX))

    def cutOnLinkProb(self, features, linkProb):
        """Clean extra information on annotation features,
        and filter out annotations with link probability lower than linkProb"""
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
            qrels, external, annotationFilter = False, bootstrap = 0, dumpsPath = None):
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
        bootstrap - number of samples to add to the training set before starting classification
        dumpsPath - path where to store serialized results
        """
        #print self.classifier, neg, external, minLinkProb, annotationFilter, bootstrap
        results = {}
        printOut = {}
        assert len(queries) == len(queriesAnnotated)
        for i, q in enumerate(queries):
            #alreadySeen = set()
            if int(q[0][2:]) not in qrels:
                continue
            #print q
            start_time = time.time()
            results[q[0]] = []
            negCount = neg
            bootstrapCount = bootstrap if bootstrap > 0 else 0
            trainingFile = open(os.path.join(trainingSetPath, q[0]))
            rawTweets=[]
            testFile = open(os.path.join(filteringIdsPath, q[0]))
            posAnnotations = set()
            # add the query as positive example
            features = self.featureExtractQuery(q[1], external)# + '\t\t' + queriesAnnotated[i][1], external)
            #features = self.cutOnLinkProb(features, self.minLinkProb)
            features_binary = self.featureExtractQueryBinary(q[1]+'\t\t' + queriesAnnotated[i][1], external)
            #features_binary = self.cutOnLinkProb(features_binary, self.minLinkProb)
            positives = [q[1]]
            #print '[Debug]', 'QUERY', features, features_binary
            # the set of features that any positive sample must contain
            initialFeatures = set(features + features_binary)
            #FIXME get annotations online
            if annotationFilter:
                posAnnotations.update(self.get_annotations(features))
            rawTweets.append((q[0], True, features, features_binary))
            # add the first tweet as positive example
            for line in testFile:
                tweetId, null, text = unicode(line, encoding='utf8').partition('\t\t')
                text = text.strip('\n')
                #alreadySeen.add(self.tweetHash(text))
                results[q[0]].append((tweetId, '1.0\tyes'))
                features = self.featureExtract(text, external)
                #features = self.cutOnLinkProb(features, self.minLinkProb)
                features_binary = self.featureExtractBinary(text, external)
                #features_binary = self.cutOnLinkProb(features_binary, self.minLinkProb)
                #print '[Debug]', 'FIRST', features, features_binary
                positives.append((tweetId, text))
                #FIXME get annotations online
                if annotationFilter:
                    posAnnotations.update(self.get_annotations(features))
                rawTweets.append((tweetId, True, features, features_binary))
                break
            for line in trainingFile:
                if negCount < 1:
                    break
                tweetId, null, text = unicode(line, encoding='utf8').partition('\t\t')
                text = text.strip('\n')
                features = self.featureExtract(text, external)
                #features = self.cutOnLinkProb(features, self.minLinkProb)
                features_binary = self.featureExtractBinary(text, external)
                #features_binary = self.cutOnLinkProb(features_binary, self.minLinkProb)
                rawTweets.append((tweetId, False, features, features_binary))
                negCount -= 1
            # add a negative sample at the axis origin
            #rawTweets.append((0, False, [], []))
            training = TrainingSet(rawTweets, 0)
            if rawTweets:
                training.mergedIndex()
                self.classifier.retrain(training.mergedMatrix, training.tweetTarget)
            #for e, v in enumerate(training.tfidfMatrix[:2]):
            #    fe = training.features[e].split(' ')
            #    col = v.nonzero()[1]
            #    for z in xrange(len(fe)):
            #        print fe[z], v[0,col[z]]
            #    print training.tweetTarget[e]
            # do not train the first tweet
            tp, fp, fn = [], [], []
            for line in testFile:
                tweetId, null, text = unicode(line, encoding='utf8').partition('\t\t')
                text = text.strip('\n')
                #currTweetHash = self.tweetHash(text)
                # exclude retweets
                if retweetRE.findall(text):# or currTweetHash in alreadySeen or viaUserRE.findall(text.split('\t\t')[0]):
                    continue
                #alreadySeen.add(currTweetHash)
                features = self.featureExtract(text, external)
                #features = self.cutOnLinkProb(features, self.minLinkProb)
                features_binary = self.featureExtractBinary(text, external)
                #features_binary = self.cutOnLinkProb(features_binary, self.minLinkProb)
                if not features or not (len(initialFeatures & set(features + features_binary))) \
                        or not hasUrl(text.split('\t\t')[0]):
                    continue
                #FIXME get annotations online
                testAnnotation = set(self.get_annotations(features))
                if annotationFilter and not posAnnotations.intersection(testAnnotation):
                    continue
                if bootstrapCount > 0:
                    if posAnnotations.intersection(testAnnotation):
                        results[q[0]].append((tweetId, '1.0\tyes'))
                        if tweetId in qrels[int(q[0][2:])][0]:
                            training.addExample((tweetId, True, features, features_binary))
                            if annotationFilter:
                                posAnnotations.update(self.get_annotations(features))
                            # TODO pop a old positive sample? only if rules are not used?
                        elif tweetId in qrels[int(q[0][2:])][1]:
                            training.addExample((tweetId, False, features, features_binary))
                    bootstrapCount -= 1
                    if bootstrapCount == 0:
                        training.mergedIndex()
                        self.classifier.retrain(training.mergedMatrix, training.tweetTarget)
                        bootstrapCount = -1
                    continue
                #nb.test(tweetId, features)
                test = training.mergedIndexTest((tweetId, False, features, features_binary))
                classification = self.classifier.classify(test)
                if classification == 1 and tweetId not in qrels[int(q[0][2:])][0]:
                    fp.append((tweetId, text))
                if classification == 0 and tweetId in qrels[int(q[0][2:])][0]:
                    fn.append((tweetId, text))
                    #print '[Debug]', tweetId, features, features_binary, 'C ' + str(classification), \
                    #    'Target '+str(tweetId in qrels[int(q[0][2:])][0])
                if classification == 1 and tweetId in qrels[int(q[0][2:])][0]:
                    tp.append((tweetId, text))
                    #print '[Debug]', 'POSITIVE', tweetId, features, features_binary
                #print classifier.getProb(test)
                if classification == 1:
                    score = self.classifier.getProb(test) if callable(getattr(self.classifier, "getProb", None)) else 1.
                    results[q[0]].append((tweetId, str(score) + '\tyes'))
                    if tweetId in qrels[int(q[0][2:])][0]:
                        training.addExample((tweetId, True, features, features_binary))
                        if annotationFilter:
                            posAnnotations.update(self.get_annotations(features))
                        # TODO pop a old positive sample? only if rules are not used?
                        training.mergedIndex()
                        self.classifier.retrain(training.mergedMatrix, training.tweetTarget)
                    #elif tweetId in qrels[int(q[0][2:])][1]:
                    else:
                        training.addExample((tweetId, False, features, features_binary))
                        training.mergedIndex()
                        self.classifier.retrain(training.mergedMatrix, training.tweetTarget)
            #print '[Debug] Query processed in ', time.time() - start_time, 'seconds.'
            testFile.close()
            printOut[q[0]] = (positives, tp, fp, fn)
            if dumpsPath:
                cPickle.dump(results[q[0]], open(os.path.join(dumpsPath, q[0]), 'w'))
        return results, printOut
