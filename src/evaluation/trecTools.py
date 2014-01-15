"""Execute TREC scripts for evaluation."""

from mb12filteval import *
import EvalJig as ej
import collections, re

def printEval(topicsPath, qrelsPath, results):

    jig = FilterJig()
    jig.add_op(ej.NumRetr())
    jig.add_op(ej.NumRel())
    jig.add_op(ej.RelRet())
    jig.minrel = 1
    jig.verbose = False
    jig.add_op(Precision())
    jig.add_op(Recall())
    jig.add_op(Fb(0.5))
    jig.add_op(T11SU())

    # Identify query tweets from the topic file
    qtweets = dict()
    tops = bs(open(topicsPath))
    for t in tops.find_all('querytweettime'):
        tnum = t.parent.num.text.strip()
        tnum = re.search(r'0*(\d+)$', tnum).group(1)
        qtweets[tnum] = t.text.strip()

    # Read in relevance judgments, dropping the querytweet
    qrels = collections.defaultdict(dict)
    with open(qrelsPath) as qrelsfile:
        for line in qrelsfile:
            topic, _, docid, rel = line.split()
            if topic not in qtweets:
                continue
            if docid == qtweets[topic]:
                continue
            qrels[topic][docid] = int(rel)

    run = collections.defaultdict(list)
    for q, res in results.iteritems():
        q = q.lstrip('MB0')
        for r in res:
            score, retrieve = r[1].split('\t')
            if retrieve == 'no':
                continue
            if r[0] == qtweets[q]:
                continue
            run[q].append((float(score), r[0]))

    for topic in qrels.iterkeys():
        jig.zero(topic)
        num_rel = sum(1 for rel in qrels[topic].values() if rel >= jig.minrel)
        if num_rel == 0:
            warn("Topic "+topic+" has no relevant documents")
            continue
        if run.has_key(topic):
            jig.compute(topic, run[topic], qrels[topic])
        else:
            jig.compute(topic, [], qrels[topic])

    jig.print_scores()
    jig.comp_means()
    jig.print_means()
