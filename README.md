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
Language training files included in data/resources/languageTraining are made for CipCipPy.utils.language.Lang class.<br/>
For hashtag segmentation it is necessary to build a dictionary {term: frequency}; 
e.g., we have used Google 1-grams http://storage.googleapis.com/books/ngrams/books/datasetsv2.html.

Dependencies
------------
* whoosh
* sklearn
* nltk
* langid (for language detection)
* TREC tools for evaluation: mb12-filteval.py and EvalJig.py 
(download them from http://trec.nist.gov/data/microblog2012.html and rename mb12-filteval.py to mb12filteval.py) 

Packages and files
------------------
* *config.py*
    Global parameters for configuring the environment.
* *corpus*
    A new corpus can be generated with the function *corpus.build*, passing a list of instances of the classes from
    *corpus.filters*.
* *indexing*
    Each module in this package contains a function *index* to generate an index from a plain text corpus, 
    filtering out documents after a specific time.
    An index takes a name that is used in the retrieval phase.
* *retrieval*
    Tools for accessing (e.g., searching) the indexes.
* *classification*
    Supervised learning utilities.
* *realtimeFilering*
    Classes for real-time filtering (a TREC microblog task), which mainly use *classification*.
* *utils*
    Generic classes and functions used in the library.
* *scripts* (not a package)
    Scripts for executing applications which exploit the library (building indexes, validating models, ...).
* *data* (not a package)
    The data path contains all the data files used by the library (cached data, indexes, ...).

Publications
------------
* *On the Impact of Entity Linking in Microblog Real-Time Filtering*. Berardi G., Ceccarelli D., Esuli A., & Marcheggiani D.
* *ISTI@ TREC Microblog track 2012: real-time filtering through supervised learning*. Berardi G., Esuli A., & Marcheggiani D.
* *ISTI@ TREC Microblog track 2011: exploring the use of hashtag segmentation and text quality ranking*. Berardi G., Esuli A., Marcheggiani D., & Sebastiani F.