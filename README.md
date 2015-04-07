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
In *config.py* set the constant DATA_PATH to the directory where CipCipPy will store data (indexes, cache, ...).
Install the package executing: python setup.py install.
Some language training files are included in data/resources/languageTraining.
For hashtag segmentation it is necessary to build a dictionary {term: frequency}, we have used Google 1-grams http://storage.googleapis.com/books/ngrams/books/datasetsv2.html.

Dependencies
------------
* numpy
* whoosh
* sklearn
* nltk
* langid (for language detection)
* httplib2 (only for corpus downloading)
* TREC tools for evaluation (only in test scripts): mb12eval, mb12filteval, EvalJig

Packages and files
------------------
* *config.py*
    Global constants to configure the environment
* *corpus*
    New corpus can be generated with the function *corpus.builder*, passing a list of instances of the classes in
    *corpus.filters*.
* *external*
    Interfaces for accessing to external resources.
* *indexing*
    Each module in this package contains a function *index* to generate an index from a plain text corpus, filtering out documents after a specific time.
    An index takes a name that is used in the retrieval phase.
* *retrieval*
    Classes for searching, use the indexes by index names.
* *classification*
    Supervised learning utilities.
* *realtimeFilering*
    Classes for real-time filtering (a TREC microblog task), they uses *classification*.
* *utils*
    Generic classes and functions used in the library.
* *test* (not a package)
    Scripts to execute applications using the library (building indexes, searching from TREC topics, ...).
* *data* (not a package)
    Data path contains all the data used by the library (cached data, indexes, ...).

Publications
------------
* *On the Impact of Entity Linking in Microblog Real-Time Filtering*. Berardi G., Ceccarelli D., Esuli A., & Marcheggiani D.
* *ISTI@ TREC Microblog track 2012: real-time filtering through supervised learning*. Berardi G., Esuli A., & Marcheggiani D.
* *ISTI@ TREC Microblog track 2011: exploring the use of hashtag segmentation and text quality ranking*. Berardi G., Esuli A., Marcheggiani D., & Sebastiani F.