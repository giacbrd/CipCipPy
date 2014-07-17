"""Generate a json dump with the entity linking information for the queries.
usage: <print out of a filtering run> <output file> <Dexter API url>"""

import json
import sys
from CipCipPy.utils.entityLink import entities
from pydexter import DexterClient

tweets = eval(open(sys.argv[1]).readline().strip())
out_path = sys.argv[2]
dxtr = DexterClient(sys.argv[3], default_params={"lp":0.1})

ann_tweets = {}

for q in tweets:
    tweet = tweets[q][0][1][1].split("\t\t")
    ann_tweets[q] = (entities(tweet[0], dxtr, 0.1), entities(tweet[2], dxtr, 0.1))

with open(out_path, "w") as out_file:
    json.dump(ann_tweets, out_file)