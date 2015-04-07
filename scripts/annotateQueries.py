"""Generate a json dump with the entity linking information for the queries.
usage: <topic file> <output file> <Dexter API url>"""

import json
import sys
from CipCipPy.utils.io import readQueries
from CipCipPy.utils.annotation import entities
from pydexter import DexterClient

queries = readQueries(sys.argv[1])
out_path = sys.argv[2]
dxtr = DexterClient(sys.argv[3], default_params={"lp":0.2})

ann_queries = {}

for q in queries:
    ann_queries[q[0]] = entities(q[1], dxtr, 0.2)

with open(out_path, "w") as out_file:
    json.dump(ann_queries, out_file)