"""Filter classes to use in this package builder method."""

from ..utils import language
import re
import urllib2
import signal


class BaseFilter:
    
    def filter(self, line):
        l = line.split('\t')
        if l[3] != 'null' and l[2] != '302':
            return line
        else:
            return None

class TimeRange:

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
    def __init__(self):
        self.lingGuesser = language.Lang('ling/languageTraining')
    
    def filter(self, line):
        if self.lingGuesser.guess(line.split('\t')[-1]) == 'english':
            return line
        else:
            return None


class LinkTitles:
    """Substitute the twitter status with the titles of links it contains."""
    
    class TimeoutException(Exception): 
        pass
    def timeout_handler(signum, frame):
        raise TimeoutException()
    
    def getTitle(url):
        oldHandler = signal.signal(signal.SIGALRM, timeout_handler) 
        signal.alarm(90)
        try: 
            u = urllib2.urlopen(url)
            if u:
                html = u.read()
                titles = re.findall(r'<title>(.+)</title>', html, re.I)
                if len(titles) > 0:
                    return '\t'.join(titles)
        except TimeoutException:
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
            if urls[i][-1] in puncts:
                urls[i] = urls[i][:-1]
        if len(urls) > 0:
            l[4] = '\t'.join(getTitle(url) for url in urls)
            return '\t'.join(l) + '\n'
        else:
            return None