"""
CipCipPy

Constants used in CipCipPy
"""

import os

# DEFINE THE DATA PATH!
DATA_PATH = '/pathTo/CipCipPy/data'

# Dexter REST API server url
DEXTER_URL = "http://ilona.isti.cnr.it:8080/dexter-webapp/api/"

CACHE_PATH = os.path.join(DATA_PATH, 'cache')
INDEX_PATH = os.path.join(DATA_PATH, 'indexes')
RESOURCE_PATH = os.path.join(DATA_PATH, 'resources')

#TODO these constants should be parameters
PROC_NUM = 1  # number of processors for indexing computing
MEM_SIZE = 1024  # memory size for each processor in indexing computing, in MB
