"""Interface to interactive interface console with Naive Bayes implementation in the Jatecs library"""

from ..utils.process import InteractiveProcess, InteractiveProcessException

class NBInterface(InteractiveProcess):

    def __init__(self, jatecsApp):
        InteractiveProcess.__init__(self, jatecsApp)
        output = self.communicate('INIT +')
        if output != 'OK':
            raise InteractiveProcessException(output)

    def train(self, tweetId, positive, features):
        """Add a tweet to the training set.
         positive is True the tweet belongs to the category, features is an iterator of strings."""
        output = self.communicate('INDEX TRAIN ' + str(tweetId) + ' ' + ('+' if positive else '') + ' | ' + ' '.join(features))
        if output == 'OK':
            return True
        else:
            raise InteractiveProcessException(output)

    def test(self, tweetId, features):
        """Add a tweet to the test set.
         features is an iterator of strings."""
        output = self.communicate('INDEX TEST ' + str(tweetId) + ' | ' + ' '.join(features))
        if output == 'OK':
            return True
        else:
            raise InteractiveProcessException(output)

    def learn(self):
        """Learn the classifier from the current training set."""
        output = self.communicate('LEARN NB')
        if output == 'OK':
            return True
        else:
            raise InteractiveProcessException(output)

    def clearTest(self):
        """Clear the current test set."""
        output = self.communicate('CLEAR TEST')
        if output == 'OK':
            return True
        else:
            raise InteractiveProcessException(output)

    def classify(self):
        """Learn the classifier from the current training set."""
        classification = {}
        output = self.communicate('CLASSIFY')
        if 'ERROR' in output:
            raise InteractiveProcessException(output)
        else:
            tweetsCount = int(output.split(' ')[0])
            for i in xrange(tweetsCount):
                line = self.proc.stdout.readline().strip().split(' ')
                classification[line[0]] = float(line[2]) - 0.5
            return classification
