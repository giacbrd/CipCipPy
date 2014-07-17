"""Classification with scikit-learn"""

import scipy.spatial.distance
import numpy as np
from scipy.sparse import csr_matrix, issparse

import sklearn
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn import svm
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.neighbors import NearestCentroid, KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import RidgeClassifier, LogisticRegression



class TrainingSet():

    def __init__(self, rawTweets, tweetsToPop):
        """rawTweets is the initial training set, the first tweetsToPop tweets can be successively removed to refine
        the training set, for example after a new sample is added to it"""
        self.tweetId = []
        self.tweetTarget = []
        self.features = []
        #self.featuresBinary = []
        self.tweetsToPop = tweetsToPop
        for tweet in rawTweets:
            self.tweetId.append(tweet[0])
            self.tweetTarget.append(1 if tweet[1] else 0)
            self.features.append(' '.join(tweet[2]))
            #self.featuresBinary.append(' '.join(triple[3]))
        self.tfidfMatrix = None
        #self.binaryMatrix = None
        #self.binary_count_vect = CountVectorizer(lowercase=False, binary=True, min_df=1)
        # self.count_vect = CountVectorizer(lowercase=False)
        # self.idf_transf = TfidfTransformer()
        self.tfidf_vect = TfidfVectorizer(lowercase=False, min_df=1, binary=False)
        self.mergedMatrix = None
        #self.has_binary = True


    def countVectorizeTfIdf(self):
        """Compute vectors of features presence (binary count), and inverse document frequency"""
        self.tfidfMatrix = self.tfidf_vect.fit_transform(self.features)


    # def countVectorizeBinary(self):
    #     """Compute vectors of binary features"""
    #     self.binaryMatrix = self.binary_count_vect.fit_transform(self.featuresBinary)


    def vectorizeTestTfIdf(self, testTweet):
        """Vectorize a tweet with idf"""
        return self.tfidf_vect.transform([' '.join(testTweet[2])])


    # def vectorizeTestBinary(self, testTweet):
    #     """Vectorize a tweet with binary features"""
    #     return self.binary_count_vect.transform([' '.join(testTweet[3])])


    def mergedIndex(self):
        """Creates and merge the idf matrix and the binary matrix """
        # self.countVectorizeTfIdf()
        # if not [item for sublist in self.featuresBinary for item in sublist]:
        #     self.has_binary = False
        #     self.mergedMatrix = self.tfidfMatrix
        # else:
        #     self.countVectorizeBinary()
        #     self.mergedMatrix = np.concatenate((self.tfidfMatrix.todense(), self.binaryMatrix.todense()), axis=1)
            # self.tfidfMatrix = np.csc_matrix(self.tfidfMatrix)
        self.countVectorizeTfIdf()
        self.mergedMatrix = self.tfidfMatrix


    def mergedIndexTest(self, testTweet):
        """Creates and merge the idf vector and the binary vector """
        # idfTestVector = self.vectorizeTestTfIdf(testTweet)
        # if not self.has_binary:
        #     return idfTestVector
        # else:
        #     binaryTestVector = self.vectorizeTestBinary(testTweet)
        #     return np.concatenate((idfTestVector.todense(), binaryTestVector.todense()), axis=1)
        return self.vectorizeTestTfIdf(testTweet)


    def addExample(self, rawTweet):
        """Add a new example for retraining"""
        self.tweetId.append(rawTweet[0])
        self.tweetTarget.append(1 if rawTweet[1] else 0)
        self.features.append(' '.join(rawTweet[2]))
        # if self.has_binary:
        #     self.featuresBinary.append(' '.join(rawTweet[3]))

    def popOldExample(self):
        """Pop out the first example inserted"""
        if self.tweetsToPop > 0:
            self.tweetId.pop(0)
            self.tweetTarget.pop(0)
            self.features.pop(0)
            self.tweetsToPop -= 1




########################################################################################


class Classifier(object):

    def retrain(self, vectorFeature, vectorTarget):
        self.cl.fit(vectorFeature, vectorTarget)

    def classify(self, vectorizedTest):
        return self.cl.predict(vectorizedTest)[0]

class ProbClassifier(object):

    def getProb(self, vectorizedTest):
        return self.cl.predict_proba(vectorizedTest)[0][1]


class NBClassifier(Classifier, ProbClassifier):

    def __init__(self):
        self.cl = MultinomialNB()


class SVMClassifier(Classifier):

    def __init__(self):
        self.cl = svm.SVC()


class OneClassClassifier(Classifier):

    def __init__(self, nu=0.5):
        self.cl = svm.OneClassSVM(nu=nu)

    def retrain(self, vectorFeature, vectorTarget):
        assert(vectorFeature.shape[0] == len(vectorTarget))
        trueRows = [i for i, t in enumerate(vectorTarget) if t]
        # get the rows with target==1 (positive samples)
        vectors = vectorFeature[trueRows, :]
        self.cl.fit(vectors)


class KNNClassifier(Classifier, ProbClassifier):

    def __init__(self, neighbors=2):
        self.cl = KNeighborsClassifier(n_neighbors=neighbors)


class ADAClassifier(Classifier, ProbClassifier):

    def __init__(self, maxTreeDepth=1, estimators=50, learningRate=1.):
        self.cl = AdaBoostClassifier(n_estimators=estimators, learning_rate=learningRate,
                                      base_estimator=DecisionTreeClassifier(max_depth=maxTreeDepth))

    def retrain(self, vectorFeature, vectorTarget):
        # self.cl.fit([v.toarray()[0] for v in vectorFeature], vectorTarget)
        self.cl.fit(vectorFeature, vectorTarget)

    def classify(self, vectorizedTest):
        # return self.cl.predict(vectorizedTest.toarray()[0])[0]
        return self.cl.predict(vectorizedTest)[0]

    def getProb(self, vectorizedTest):
        # return self.cl.predict_proba(vectorizedTest.toarray()[0])[0][1]
        return self.cl.predict_proba(vectorizedTest)[0][1]

class RClassifier(Classifier):
    """Ridge classifier"""
    def __init__(self, alpha=1.):
        self.cl = RidgeClassifier(alpha=alpha)

class LClassifier(Classifier):

    def __init__(self, C=1.):
        self.cl = LogisticRegression(C=C, class_weight='auto', penalty='l2')


class NCClassifier(Classifier):
    """Rocchio classifier"""
    def __init__(self, shrink=None):
        self.cl = NearestCentroid(shrink_threshold=shrink)
        self.shrink = shrink

    def retrain(self, vectorFeature, vectorTarget):
        if self.shrink != None:
            self.cl.fit([v.toarray()[0] for v in vectorFeature], vectorTarget)
        else:
            super(NCClassifier, self).retrain(vectorFeature, vectorTarget)

    def classify(self, vectorizedTest):
        if self.shrink != None:
            return self.cl.predict(vectorizedTest.toarray()[0])[0]
        else:
            return super(NCClassifier, self).classify(vectorizedTest)

class RocchioClassifier(Classifier):
    """Rocchio classifier"""
    def __init__(self, threshold = 0.5, distance_func = scipy.spatial.distance.cosine):
        self.threshold = threshold
        self.distance_func = distance_func

    def retrain(self, vectorFeature, vectorTarget):
        assert(vectorFeature.shape[0] == len(vectorTarget))
        trueRows = [i for i, t in enumerate(vectorTarget) if t]
        # get the rows with target==1 (positive samples)
        vectors = vectorFeature[trueRows, :]
        #self.centroid = csr_matrix(vectors.mean(0))
        self.centroid = vectors.mean(0)

    def classify(self, vectorizedTest):
        if issparse(vectorizedTest):
            vectorizedTest = vectorizedTest.toarray()
        if self.distance_func(vectorizedTest, self.centroid) < self.threshold:
            return 1
        else:
            return 0

class NegativeRocchioClassifier(Classifier):
    """Rocchio classifier"""
    def __init__(self, threshold = 0.5, distance_func = scipy.spatial.distance.cosine):
        self.threshold = threshold
        self.distance_func = distance_func
        self.neg_centroid = np.zeros(1)

    def retrain(self, vectorFeature, vectorTarget):
        assert(vectorFeature.shape[0] == len(vectorTarget))
        #FIXME operations on sparse matrices
        pos_rows = [i for i, t in enumerate(vectorTarget) if t]
        neg_rows = [i for i, t in enumerate(vectorTarget) if not t]
        # get the rows with target==1 (positive samples)
        pos_vectors = vectorFeature[pos_rows, :]
        neg_vectors = [v.toarray() for v in vectorFeature[neg_rows, :] if v.getnnz()]
        self.pos_centroid = pos_vectors.mean(0)
        if not self.neg_centroid.any() and self.neg_centroid.shape[0] != self.pos_centroid.shape[0]:
            self.neg_centroid = np.zeros(self.pos_centroid.shape[0])
        else:
            #FIXME efficiency!
            self.neg_centroid = np.array([v for v in neg_vectors if self.distance_func(v, self.pos_centroid) > self.threshold]).mean(0)

    def classify(self, vectorizedTest):
        if issparse(vectorizedTest):
            vectorizedTest = vectorizedTest.toarray()
        #FIXME optime!
        pos_dist = self.distance_func(vectorizedTest, self.pos_centroid)
        neg_dist = self.distance_func(vectorizedTest, self.neg_centroid)
        return 1 if pos_dist < neg_dist else 0

class DTClassifier(Classifier):
    """Decision Tree classifier"""
    def __init__(self):
        self.cl = DecisionTreeClassifier(random_state=0)


class RFClassifier(Classifier):
    """Random forest classifier"""
    def __init__(self):
        self.cl = RandomForestClassifier(n_jobs=2)


class idfVectorizer():
    """Vectorizes a dataset with its IDF weights, same behaviour of TFIDF vectorizer"""
    def __init__(self):
        self.binary_vect = CountVectorizer(lowercase=False, binary=True, min_df=1)
        self.idf_transf = TfidfTransformer()

    def fit_transform(self, dataset):
        return self.idf_transf.transform(self.binary_vect.fit_transform(dataset))

    def fit(self, dataset):
        return self.binary_vect.fit(dataset)

    def transform(self, dataset):
        return self.idf_transf.transform(self.binary_vect.transform(dataset))