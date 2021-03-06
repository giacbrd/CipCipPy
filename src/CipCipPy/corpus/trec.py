"""Methods for managing the corpus using the official https://github.com/lintool/twitter-corpus-tools"""

import os
import subprocess

def _getCommand(toolsDir, toolsJar):
    return "java -Xmx4g -cp '" + toolsDir + "/lib/*:" + toolsDir + "/dist/twitter-corpus-tools-0.0.1.jar' "


def download(toolsPath, toolsJar, datPath, outPath):
    command = _getCommand(toolsPath)
    for names in os.walk(datPath):
        for fName in names[2]:
            if fName[-3:] == 'dat':
                subprocess.check_call((
                    command + " com.twitter.corpus.download.AsyncHtmlStatusBlockCrawler -data " + os.path.join(names[0],
                        fName) + " -output " + os.path.join(outPath, fName[:-4] + ".html.seq")), shell=True)


def dump(toolsPath, toolsJar, corpusPath, outPath):
    command = _getCommand(toolsPath)
    for names in os.walk(corpusPath):
        for fName in names[2]:
            if fName[-3:] == 'seq':
                subprocess.check_call((
                    command + " com.twitter.corpus.demo.ReadStatuses -input " + os.path.join(names[0],
                        fName) + " -dump -html > " + os.path.join(outPath, fName[:-4] + ".txt")), shell = True)


def repair(toolsPath, toolsJar, datPath, corpusPath, outPath, logsPath):
    command = _getCommand(toolsPath)
    for names in os.walk(datPath):
        for fName in names[2]:
            if fName[-3:] == 'dat':
                subprocess.check_call((
                    command + " com.twitter.corpus.download.VerifyHtmlStatusBlockCrawl -data " + os.path.join(names[0],
                        fName) + " -statuses_input " + os.path.join(corpusPath,
                        fName[:-4] + ".html.seq") + " -statuses_repaired " + os.path.join(outPath,
                        fName[:-4] + ".html.seq") + " -output_success " + os.path.join(logsPath,
                        "log.success") + " -output_failure " + os.path.join(logsPath, "log.failure")),
                        shell=True)