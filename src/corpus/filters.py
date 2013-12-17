"""Filter classes to use in this package builder method."""

from ..utils import language, punctuations
import re
import urllib2
import signal


class BaseFilter:
    """Filter out bad tweets"""
    
    def filter(self, line):
        l = line.split('\t')
        if l[3] != 'null' and l[2] != '302':
            return line
        else:
            return None

class TimeRange:
    """Filter out tweets external to a time range"""

    def __init__(self, tweetTime, tweetNewestTime):
        self.tweetTime = tweetTime
        self.tweetNewestTime = tweetNewestTime

    def filter(self, line):
        l = line.split('\t')
        time = int(l[0])
        if time >= self.tweetTime and time <= self.tweetNewestTime:
            return line
        else:
            return None


class English:
    """Filter out non english tweets."""

    # TODO pass a english corpus to verify if a tweet is already processed e.g. add only new tweets and copy the old ones
    def __init__(self, languageTraining):
        self.lingGuesser = language.Lang(languageTraining)
    
    def filter(self, line):
        if self.lingGuesser.guess(line.split('\t')[-1]) == 'english':
            return line
        else:
            return None

class English2:

    def __init__(self):
        from langid.langid import LanguageIdentifier, model
        self.identifier = LanguageIdentifier.from_modelstring(model, norm_probs=False)

    def filter(self, line):
            if self.identifier.classify(line.split('\t')[-1])[0] == 'en':
                return line
            else:
                return None


class LinkTitles:
    """Substitute the twitter status with the titles of links it contains."""
    
    class TimeoutException(Exception): 
        pass

    def timeout_handler(self, signum, frame):
        raise self.TimeoutException()
    
    def getTitle(self, url):
        oldHandler = signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(15)
        try: 
            u = urllib2.urlopen(url)
            if u:
                html = u.read()
                titles = re.findall(r'<title>(.+)</title>', html, re.I)
                if len(titles) > 0:
                    return '\t'.join(titles)
        except self.TimeoutException:
            print 'timeout: ', url
        except Exception as err:
            print 'error:', url, '\n' + str(err)
        finally:
            signal.signal(signal.SIGALRM, oldHandler)
            signal.alarm(0)
    
    def filter(self, line):
        l = line.split('\t')
        urls = re.findall(r'(http://\S+)', l[4])
        for i in xrange(len(urls)):
            if urls[i][-1] in punctuations:
                urls[i] = urls[i][:-1]
        if len(urls) > 0:
            l[4] = '\t'.join(self.getTitle(url) for url in urls)
            return '\t'.join(l) + '\n'
        else:
            return None