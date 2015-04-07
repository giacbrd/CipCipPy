#    CipCipPy - Twitter IR system for the TREC Microblog track.
#    Copyright (C) <2011-2015>  Giacomo Berardi, Andrea Esuli, Diego Marcheggiani
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

Generic instruments for CipCipPy.
"""

__version__ = "0.2"
__authors__ = ["Giacomo Berardi <giacomo.berardi@isti.cnr.it>", 
               "Andrea Esuli <andrea.esuli@isti.cnr.it>", 
               "Diego Marcheggiani <diego.marcheggiani@isti.cnr.it>"]

import re, string, hashlib

punctuations = set(string.punctuation)

months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

hashtagRE = re.compile('#(\S+)')
# TODO some characters must be excluded, like ':' at the end of a username of a reply
replyRE = re.compile('@(\S+)')
hashReplRE = re.compile('[@|#]\S+')
urlRE = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', re.IGNORECASE)
viaUserRE = re.compile("via @(\S+)", re.IGNORECASE)
retweetRE = re.compile("^RT @", re.IGNORECASE)
wordDotsRE = re.compile("\S+\.\.+", re.IGNORECASE)

def substPunct(text, subst = ''):
    return ''.join(c if c not in punctuations else subst for c in text)

def queryNumToId(q):
    """Returns the query id string from an integer id"""
    return 'MB{num:03d}'.format(num=q)

def queryIdToNum(q):
    """Returns the query id integer from an string id"""
    return int(q[2:])

def textHash(text):
    """hash integer of a string"""
    return int(hashlib.md5(text.encode('ascii', 'replace')).hexdigest()[:12], 16)

stopwords = frozenset(("secondly", "all",
					"consider", "whoever", "go", "evermore", "causes",
					"seemed", "rd", "certainly", "when's", "to", "th", "under",
					"a's", "every", "yourselves", "we'll", "went", "did",
					"forth", "they've", "fewer", "try", "one's", "it'll",
					"i'll", "says", "you'd", "yourself", "likely",
					"notwithstanding", "further", "even", "what", "goes",
					"ever", "c'mon", "whose", "respectively", "never", "let",
					"others", "hadn't", "along", "aren't", "ahead", "k", "i'd",
					"howbeit", "he'd", "whereupon", "i'm", "thats", "hither",
					"via", "followed", "merely", "while", "till", "viz",
					"everybody", "use", "from", "would", "contains", "two",
					"next", "few", "therefore", "taken", "themselves", "thru",
					"tell", "more", "mr", "becomes", "hereby", "herein",
					"ain't", "who'll", "me", "none", "this", "oh", "anywhere",
					"can", "theirs", "following", "my", "neverf", "didn't",
					"something", "want", "rather", "meanwhile", "makes", "how",
					"opposite", "instead", "okay", "tried", "after",
					"hereupon", "whilst", "such", "undoing", "a", "whenever",
					"maybe", "so", "that's", "don't", "indeed", "over",
					"mainly", "course", "through", "its", "before", "he's",
					"selves", "inward", "actually", "whether", "willing",
					"ours", "might", "haven't", "then", "non", "someone",
					"somebody", "thereby", "underneath", "you've", "they",
					"not", "nor", "several", "hereafter", "reasonably",
					"whither", "she's", "each", "found", "entirely", "mustn't",
					"isn't", "everyone", "directly", "doing", "eg", "our",
					"beyond", "them", "needn't", "furthermore", "looking",
					"re", "shouldn't", "they'll", "got", "thereupon", "you're",
					"given", "what'll", "que", "besides", "what've", "ask",
					"anyhow", "backwards", "could", "tries", "keep", "caption",
					"ltd", "hence", "onto", "think", "already", "seeming",
					"thereafter", "one", "done", "another", "awfully",
					"doesn't", "their", "accordingly", "least", "anyone",
					"indicate", "too", "gives", "mostly", "behind", "nobody",
					"took", "immediate", "regards", "somewhat", "kept",
					"believe", "herself", "than", "here's", "unfortunately",
					"gotten", "i", "were", "toward", "minus", "are", "and",
					"alongside", "beforehand", "mine", "say", "unlikely",
					"have", "need", "seen", "seem", "any", "relatively",
					"abroad", "thoroughly", "latter", "that", "downwards",
					"aside", "thorough", "also", "take", "which", "begin",
					"exactly", "unless", "shall", "who", "where's", "most",
					"but", "nothing", "why", "forever", "especially", "noone",
					"later", "yours", "you'll", "definitely", "neverless",
					"she'd", "normally", "came", "saying", "particularly",
					"anyway", "that'll", "daren't", "should", "only", "going",
					"specify", "there've", "do", "his", "above", "get",
					"between", "overall", "truly", "they'd", "oughtn't",
					"cannot", "nearly", "despite", "during", "him",
					"regarding", "amid", "qv", "mayn't", "twice", "she",
					"contain", "won't", "where", "up", "namely", "anyways",
					"that've", "no-one", "wonder", "said", "there'd", "away",
					"currently", "please", "enough", "there's", "various",
					"hopefully", "probably", "neither", "across", "we",
					"recently", "however", "meantime", "come", "both", "last",
					"many", "wouldn't", "thence", "according", "etc", "became",
					"com", "can't", "otherwise", "among", "presumably", "co",
					"afterwards", "seems", "whatever", "couldn't", "moreover",
					"throughout", "considering", "it's", "been", "whom",
					"there're", "much", "wherein", "likewise", "hardly",
					"it'd", "wants", "corresponding", "latterly", "concerning",
					"else", "hers", "former", "those", "myself", "look",
					"unlike", "these", "will", "near", "taking", "theres",
					"whereafter", "almost", "wherever", "is", "thus", "it",
					"cant", "itself", "in", "ie", "if", "perhaps", "insofar",
					"make", "same", "clearly", "beside", "when", "gets",
					"weren't", "fairly", "used", "see", "somewhere", "upon",
					"uses", "he'll", "off", "whereby", "nevertheless", "whole",
					"nonetheless", "well", "anybody", "obviously", "without",
					"comes", "very", "the", "self", "lest", "things", "she'll",
					"just", "less", "being", "able", "liked", "regardless",
					"yes", "yet", "unto", "farther", "we've", "had", "except",
					"has", "adj", "ought", "t's", "around", "who's",
					"possible", "whichever", "know", "using", "who'd", "dare",
					"apart", "necessary", "like", "follows", "either",
					"become", "whomever", "towards", "therein", "why's",
					"because", "often", "some", "somehow", "specified",
					"ourselves", "shan't", "happens", "provided", "there'll",
					"for", "though", "per", "everything", "does", "provides",
					"tends", "be", "mightn't", "nowhere", "although", "by",
					"on", "about", "ok", "anything", "getting", "of", "v",
					"whence", "plus", "consequently", "or", "seeing", "own",
					"formerly", "into", "within", "down", "appropriate", "c's",
					"your", "how's", "her", "there", "amidst", "inasmuch",
					"inner", "forward", "was", "himself", "elsewhere", "i've",
					"becoming", "amongst", "back", "hi", "trying", "with",
					"he", "they're", "made", "wasn't", "wish", "inside",
					"hasn't", "us", "until", "placed", "below", "un", "we'd",
					"gone", "sometimes", "certain", "am", "an", "as",
					"sometime", "at", "et", "mrs", "inc", "again", "no",
					"whereas", "nd", "lately", "other", "you", "really",
					"what's", "let's", "upwards", "ago", "together", "having",
					"we're", "everywhere", "backward", "once", "http",
					"ah", "eh", "ha", "ho", "rt", "t", "follow", "s",
					"watch", "don", "gt", "im", "lt", "m", "u",
					"told", "ll", "here"))