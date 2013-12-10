"""Classification with scikit-learn"""

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn import svm

class TrainingSet():

    def __init__(self, rawTweets, tweetsToPop):
        """rawTweets is the initial training set, the first tweetsToPop tweets can be successively removed to refine
        the training set, for example after a new sample is added to it"""
        self.tweetId=[]
        self.tweetTarget=[]
        self.features=[]
        self.tweetsToPop = tweetsToPop
        for triple in rawTweets:
            self.tweetId.append(triple[0])
            self.tweetTarget.append(1 if triple[1] else 0)
            self.features.append(' '.join(triple[2]))
        self.vectorcounts = None
        self.count_vect = CountVectorizer(min_df=1, binary=True)
        self.idf_transf = TfidfTransformer()

    def countVectorize(self):
        """Compute vectors of features presence (binary count), and inverse document frequency"""
        self.vectorcounts = self.count_vect.fit_transform(self.features)
        self.vectoridf = self.idf_transf.fit_transform(self.vectorcounts)

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


class NBClassifier():
    def __init__(self, vectorFeature,vectorTarget):
        self.NB=MultinomialNB()
        self.NB.fit(vectorFeature, vectorTarget)

    def retrain(self, vectorFeature, vectorTarget):
        self.NB.fit(vectorFeature, vectorTarget)

    def classify(self, vectorizedTest):
        return self.NB.predict(vectorizedTest)

    def getProb(self, vectorizedTest):
        return self.NB.predict_proba(vectorizedTest)

class SVMClassifier():
    def __init__(self, vectorFeature, vectorTarget):
        self.SVM=svm.SVC()
        self.SVM.fit(vectorFeature, vectorTarget)

    def retrain(self, vectorFeature, vectorTarget):
        self.SVM.fit(vectorFeature, vectorTarget)

    def classify(self, vectorizedTest):
        return self.SVM.predict(vectorizedTest)