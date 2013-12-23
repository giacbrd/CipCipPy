"""Classification with scikit-learn"""

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn import svm, neighbors
from sklearn.ensemble import AdaBoostClassifier
from sklearn.neighbors import NearestCentroid
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import RidgeClassifier


class TrainingSet():

    def __init__(self, rawTweets, tweetsToPop):
        """rawTweets is the initial training set, the first tweetsToPop tweets can be successively removed to refine
        the training set, for example after a new sample is added to it"""
        self.tweetId = []
        self.tweetTarget = []
        self.features = []
        self.tweetsToPop = tweetsToPop
        for triple in rawTweets:
            self.tweetId.append(triple[0])
            self.tweetTarget.append(1 if triple[1] else 0)
            self.features.append(' '.join(triple[2]))
        self.vectoridf = None
        self.count_vect = CountVectorizer(min_df=1, binary=False)
        self.idf_transf = TfidfTransformer()

    def countVectorize(self):
        """Compute vectors of features presence (binary count), and inverse document frequency"""
        vectorcounts = self.count_vect.fit_transform(self.features)
        self.vectoridf = self.idf_transf.fit_transform(vectorcounts)

    def vectorizeTest(self, testTweet):
        """Vectorize a tweet with idf"""
        return self.idf_transf.transform(self.count_vect.transform([' '.join(testTweet[2])]))

    def addExample(self, rawTweet):
        """Add a new example for retraining"""
        self.tweetId.append(rawTweet[0])
        self.tweetTarget.append(1 if rawTweet[1] else 0)
        self.features.append(' '.join(rawTweet[2]))

    def popOldExample(self):
        """Pop out the first example inserted"""
        if self.tweetsToPop > 0:
            self.tweetId.pop(0)
            self.tweetTarget.pop(0)
            self.features.pop(0)
            self.tweetsToPop -= 1

class Classifier:

    def retrain(self, vectorFeature, vectorTarget):
        self.cl.fit(vectorFeature, vectorTarget)

    def classify(self, vectorizedTest):
        return self.cl.predict(vectorizedTest)[0]

    def getProb(self, vectorizedTest):
        return self.cl.predict_proba(vectorizedTest)[0][1]


class NBClassifier(Classifier):

    def __init__(self):
        self.cl = MultinomialNB()


class SVMClassifier(Classifier):

    def __init__(self):
        self.cl = svm.SVC()
        delattr(self, 'getProb')


class KNNClassifier(Classifier):

    def __init__(self, neighbors=3):
        self.cl = neighbors.KNeighborsClassifier(n_neighbors=neighbors)


class ADAClassifier(Classifier):

    def __init__(self, maxTreeDepth = 1, estimators=50, learningRate = 1.):
        self.cl = AdaBoostClassifier(n_estimators=estimators, learning_rate=learningRate,
                                      base_estimator=DecisionTreeClassifier(max_depth=maxTreeDepth))

    def retrain(self, vectorFeature, vectorTarget):
        self.cl.fit([v.toarray()[0] for v in vectorFeature], vectorTarget)

    def classify(self, vectorizedTest):
        return self.cl.predict(vectorizedTest.toarray()[0])[0]

    def getProb(self, vectorizedTest):
        return self.cl.predict_proba(vectorizedTest.toarray()[0])[0][1]


class RClassifier():

    def __init__(self, alpha = 1.):

        self.cl = RidgeClassifier(alpha=alpha)


class NCClassifier():

    def __init__(self, shrink = None):

        self.cl = NearestCentroid(shrink_threshold=shrink)