# CipCipPy
# Twitter IR system for the TREC Microblog track.
#
# Authors: Giacomo Berardi <giacomo.berardi@isti.cnr.it>
#          Andrea Esuli <andrea.esuli@isti.cnr.it>
#          Diego Marcheggiani <diego.marcheggiani@isti.cnr.it>
# URL: <http://tag.isti.cnr.it/cipcippy/>
# For license information, see LICENSE

"""
CipCipPy

System evaluation tools.
"""

__version__ = "0.1"
__authors__ = ["Giacomo Berardi <giacomo.berardi@isti.cnr.it>",
               "Andrea Esuli <andrea.esuli@isti.cnr.it>",
               "Diego Marcheggiani <diego.marcheggiani@isti.cnr.it>"]


import numpy

def ROC(results, qrels):
    """Return the ROC curves, for each query, computed on each threshold on the result scores.
    qrels is a list of relevance judgments for each result."""
    curves = []
    for q, result in results.iteritems():
        q = int(q[2:])
        if q not in qrels:
            continue
        thresholds = set(r[1] for r in result)
        points = set(((0., 0.), (1., 1.)))
        for threshold in thresholds:
            tp = 0.
            fp = 0.
            for r in result:
                if r[1] > threshold:
                    if r[0] in qrels[q][0]:
                        tp += 1.
                    else:
                        fp += 1.
            tpRate = tp / len(qrels[q][0])
            fpRate = fp / len(qrels[q][1])
            points.add((fpRate, tpRate))
        curves.append(sorted(points))
    return curves

def AUC(points):
    xy = zip(*points)
    return numpy.trapz(xy[1], xy[0])

def T11SU(results, qrels):
    evals = []
    for q, result in results.iteritems():
        q = int(q[2:])
        if q not in qrels:
            continue
        tp, fp = 0., 0.
        for r in result:
            if 'yes' in r[1]:
                if r[0] in qrels[q][0]:
                    tp += 1.
                else:
                    fp += 1.
        T11U = 2. * tp - fp
        maxU = 2. * len(qrels[q][0])
        T11NU = T11U / maxU
        evals.append((max(T11NU, -0.5) + 0.5) / 1.5)
    return evals

def F1(results, qrels):
    evals = []
    for q, result in results.iteritems():
        q = int(q[2:])
        if q not in qrels:
            continue
        tp, fp = 0., 0.
        for r in result:
            if 'yes' in r[1]:
                if r[0] in qrels[q][0]:
                    tp += 1.
                else:
                    fp += 1.
        fn = len(qrels[q][0]) - tp
        evals.append((2.* tp) / (2. * tp + fp + fn))
    return evals
