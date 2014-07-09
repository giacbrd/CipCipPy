"""Hashtag management tools"""

import re
import pickle
import sys

class Segmenter:
    
    def __words(self, text):
        return re.findall('[a-z]+', text.lower()) 
    
    def __wordProb(self, word):
        return self.dictionary.get(word, 0) / self.total
    
    def __init__(self, dictionary):
        """dictionary is a map of terms and frequency values (a dict file, serialized with pickle).
        It can be generated from a generic text, and it is used for segmentation."""
        #dictionary=open(os.path.join(RESOURCE_PATH, '1gramsGoogle'),'r')
        self.dictionary = pickle.load(open(dictionary))
        self.maxWordLength = max(map(len, self.dictionary))
        self.total = float(sum(self.dictionary.values()))


    def get(self, text):
        """Segment the hashtag text"""
        text=text.lower()
        probs, lasts = [1.0], [0]
        for i in range(1, len(text) + 1):
            prob_k, k = max((probs[j] * self.__wordProb(text[j:i]), j)
            for j in range(max(0, i - self.maxWordLength), i))
            probs.append(prob_k)
            lasts.append(k)
        words = []
        i = len(text)
        while 0 < i:
            words.append(text[lasts[i]:i])
            i = lasts[i]
        words.reverse()
        return words, probs[-1]


if __name__ == '__main__':
    se = Segmenter(sys.argv[1])
    print se.get('skypeisnotworkingagain')
    print se.get('mamamiahereicomeagain')
    print se.get('blacksabbathrocks')
    print se.get('facebookisnotworking')
