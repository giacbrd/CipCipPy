CipCipPy
========

Twitter IR system for the TREC Microblog track.

Authors:
* Giacomo Berardi <giacomo.berardi@isti.cnr.it>
* Andrea Esuli <andrea.esuli@isti.cnr.it>
* Diego Marcheggiani <diego.marcheggiani@isti.cnr.it>

For license information see LICENSE

Installation
------------
In *config.py* set the constant `DATA_PATH` with the directory where CipCipPy will store data (indexes, cache, ...).

Install the package executing: `python setup.py install`.

Some hints:<br/>
Language training files included in data/resources/languageTraining are made for *CipCipPy.utils.language.Lang* class.<br/>
For hashtag segmentation it is necessary to build a dictionary {term: frequency}; 
e.g., we have used Google 1-grams http://storage.googleapis.com/books/ngrams/books/datasetsv2.html.

Dependencies
------------
* whoosh
* sklearn
* nltk
* pydexter (http://github.com/giacbrd/pydexter)
* langid (for language detection)
* TREC tools for evaluation: mb12-filteval.py and EvalJig.py 
(download them from http://trec.nist.gov/data/microblog2012.html and rename mb12-filteval.py to mb12filteval.py) 

Packages and files
------------------
* **config.py**
    Global parameters for configuring the environment.
* **corpus**
    A new corpus can be generated with the function *corpus.build*, passing a list of instances of the classes from
    *corpus.filters*.
* **indexing**
    Each module in this package contains a function *index* for generating an index from a plain text corpus, 
    filtering out documents after a specific time.
    An index takes as argument a name that is used in the retrieval phase.
* **retrieval**
    Tools for accessing (e.g., searching) the indexes.
* **classification**
    Supervised learning utilities.
* **filtering**
    Classes for real-time filtering (a TREC microblog task), which mainly use *classification*.
* **utils**
    Generic classes and functions used in the library.
* **scripts** (not a package)
    Scripts for executing applications which exploit the library (building indexes, validating models, ...).
* **data** (not a package)
    The data path contains all the data files used by the library (cached data, indexes, ...).

Running experiments
-------------------
This guide is for real-time filtering experiments of the TREC Microblog track: 
https://sites.google.com/site/microblogtrack/2012-guidelines.
The experiments in [1] have been conducted according to this protocol.
You will need to run a [Dexter](http://www.dxtr.it) REST API server and download the files from
 http://trec.nist.gov/data/microblog2012.html.
Do not esitate to email the authors for help.

1.  First install the TREC twitter tools (http://github.com/lintool/twitter-tools) in order to download the corpus.
    You need to obtain the TREC corpus following the 
    [guidelines](http://sites.google.com/site/microblogtrack/2012-guidelines).
    CipCipPy has some tools for downloading the corpus 
    using twitter-tools, you can find them in *CipCipPy.corpus.trec*. You have to write the corpus in a directory on 
    disk in plain text files, using *CipCipPy.corpus.trec.dump*.
2.  Now you can build processed versions of the corpus, using *CipCipPy.corpus.build*, i.e. the english corpus and
    the link titles corpus. 
    Take as example the *buildCorpus.py* script, in which the filter *HtmlUnescape* is already set.
    Create three different corpus with the filters *EnglishTri*, *EnglishLangid* and *LinkTitles* 
    (the last has to be created from the final english corpus). Create
    the union of the two english corpus using *CipCipPy.corpus.enrich*, look at the *enrichCorpus.py* script as example.
3.  Corpora must be indexed in order to generate the dataset. Two scripts, *index.py* and *dataset.py*, executed in this 
    order, with proper arguments setting, will generate the final dataset. Look at the scripts code for the details.
4.  A separate script is needed for annotating query topics: *annotateQueries.py*.
5.  Finally, with *validate.py* and *test.py* you can run experiments. The first script will output a text file with 
    the evaluation of the topics file passed as argument (we created a file with the only validation topics in it).
    The second script performs a similar process and writes the dump files of the results.<br/>
    The doc string of both scripts contains details of the input arguments. An example of the model parameter string:
    RO-0.655-1000-0.2-0.1-terms.stems.bigrams.hashtags-terms.stems.bigrams-candidateEntities. 
    In *CipCipPy.clssification.feature* there is the code and the doc strings for understanding feature extraction functions.
6.  Use *evaluate.py* for printing the evaluation from result dump files.

Publications
------------
[1] On the Impact of Entity Linking in Microblog Real-Time Filtering. Berardi G., Ceccarelli D., Esuli A., & Marcheggiani D.<br/>
[2] [ISTI@ TREC Microblog track 2012: real-time filtering through supervised learning](http://trec.nist.gov/pubs/trec21/papers/NEMIS_ISTI_CNR.microblog.final.pdf). Berardi G., Esuli A., & Marcheggiani D.<br/>
[3] [ISTI@ TREC Microblog track 2011: exploring the use of hashtag segmentation and text quality ranking](http://trec.nist.gov/pubs/trec20/papers/NEMIS_ISTI_CNR.microblog.update.pdf). Berardi G., Esuli A., Marcheggiani D., & Sebastiani F.