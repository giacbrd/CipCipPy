import os

# DEFINE THE LIBRARY PATH!
ROOT_PATH = '/home/giacomo/projects/CipCipPy/'

DATA_PATH = os.path.join(ROOT_PATH, 'data')
CACHE_PATH = os.path.join(DATA_PATH, 'cache')
INDEX_PATH = os.path.join(DATA_PATH, 'indexes')
RESOURCE_PATH = os.path.join(DATA_PATH, 'resources')

#systemName = 'NeMIS' # name assigned to result files and runs
#ROOT_PATH = '/data/common/TRECmicroblog/2011/'
#RESULTS_PATH = os.path.join(ROOT_PATH, 'results/') # path of result files
#topicsFile = os.path.join(ROOT_PATH, 'data/topics.txt') # TREC topics file path

#TODO these constants should be parameters
PROC_NUM = 6  # number of processors for indexing computing
MEM_SIZE = 1024  # memory size for each processor in indexing computing, in MB
