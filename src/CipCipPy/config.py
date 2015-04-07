"""
CipCipPy

Constants used in CipCipPy
"""

import os

# DEFINE THE DATA PATH!
DATA_PATH = '/pathTo/CipCipPy/data'

CACHE_PATH = os.path.join(DATA_PATH, 'cache')
INDEX_PATH = os.path.join(DATA_PATH, 'indexes')
RESOURCE_PATH = os.path.join(DATA_PATH, 'resources')

PROC_NUM = 1  # default number of processors for indexing computing
MEM_SIZE = 1024  # default memory size for each processor in index computing, in MB
