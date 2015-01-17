import json
import urllib2
from celery import Celery
from nltk.corpus import wordnet as wn

BROKER_URL = 'redis://localhost:6379/0'

app = Celery('tasks', broker=BROKER_URL)
def classify(url, query):
    # print request
    req = urllib2.Request("https://sender.blockspring.com/api_v2/blocks/d54a2e2c28aebab4fe079ff547cea495?api_key=b93c92e09d3b2ffd8ea386a1e93ba0ea")
    req.add_header('Content-Type', 'application/json')

    data = {"img": url}

    results = urllib2.urlopen(req, json.dumps(data)).read()
    try:
        query = wn.synsets(query)[0]
    except:
        print "NO SIMS"
        return str(-1)
    # print query
    res = json.loads(results)
    sims = []
    print res
    for x in res[:5]:
        # print x
        # v = x+'.n.01'
        # print v
        try:
            s = wn.synsets(x)[0]
            # print s
            sims.append(query.path_similarity(s))
        except:
            print "COULDNT SIMS: " + str(x)
    sims = [x for x in sims if x != None]
    print sims

    for x in range(len(sims)):
        sims[x] = (((len(sims)-x)*.1)+1)*sims[x]

    print sims

    print "SCORE: " + str(sum(sims)/float(len(sims)))
    if len(sims) == 0:
        return str(-1)
    return str(sum(sims)/float(len(sims)))