import jsonrpc
import pprint
# import json
from simplejson import loads
import json
import urllib2
# import warehouse_scraper
from flask import Flask, request, redirect, url_for, \
     abort, render_template, flash, make_response, jsonify # clean these up
from nltk.corpus import wordnet as wn
from tasks import classify
app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

pp = pprint.PrettyPrinter(indent=4)

SCENE_FILE = "../Descriptions/first_demo.txt"
server = jsonrpc.ServerProxy(jsonrpc.JsonRpc20(),
        jsonrpc.TransportTcpIp(addr=("http://104.236.90.178/", 80)))
print "SERVER"
print server
f = {}
# scenes = [f for f in open(SCENE_FILE).read().split('\n') if f != '']
@app.route('/', methods=['POST'])
def get_entities():
# for scene in scenes:
    print 'here'
    global f
    scene = request.json['text']
    print scene
    print "\n"
    result = loads(server.parse(scene))
    entities = {}
    deps = []
    corefs = []
    if 'coref' in result:
        # pp.pprint(result['coref'][0][0]) 
        corefs = result['coref'][0]
    for sent in result['sentences']:
        # pp.pprint(sent['dependencies'])
        print corefs
        for dep in sent['dependencies']:
            print dep
            if dep[0] == 'det':
                entities[dep[1]] = []
            elif dep[0] == 'amod' or dep[0] == 'nsubj':
              if dep[1] in entities:
                  entities[dep[1]].append(dep[2])
              elif dep[2] in entities:
                  entities[dep[2]].append(dep[1])
            elif 'prep_' in dep[0]:
              if dep[1] == 'is': # backfill with nsubj
                try:
                  print "backfilling..."
                  print deps
                  dep[1] = [x for x in sent["dependencies"] if x[0] == 'nsubj' and x[1] == 'is'][0][2]
                  print "backfilled", dep
                except:
                  pass
              # entities[dep[1]] = dep[2]
              if dep[1] in entities and dep[2] in entities:
                  deps.append([dep[1], dep[0], dep[2]])
              else:
                  for coref in corefs:
                      obj1 = coref[0]
                      obj2 = coref[1]
                      # print obj1[0], obj2[0], dep[1]
                      if dep[1] in obj1[0]:
                          print (dep[2], dep[0], obj1[0])
                          # deps.append([dep[2], dep[0], obj[1]])
                      elif dep[1] in obj2[0]:
                          print (dep[2], dep[0], obj2[0])
                          # deps.append([obj1[0], dep[0], obj[2]])
                      elif dep[2] in obj1[0]:
                          name = [z for z in obj2[0].split() if z in entities][0]
                          deps.append([dep[1], dep[0], name])
                          # deps.append([obj2[0], dep[0], dep[1]])
                      elif dep[2] in obj2[0]:
                          name = [z for z in obj2[0].split() if z in entities][0]

                          deps.append([dep[1], dep[0], name])

                          # deps.append([obj1[0], dep[0], dep[1]])

    # deps = set(deps)
    f = {}
    pp.pprint(entities)
    print "\n"
    pp.pprint(deps)
    print "\n"
    f['entities'] = entities
    f['deps'] = deps
    return jsonify(f)


@app.route('/latest', methods=['POST', 'GET'])
def get_latest():
    return jsonify(f)


@app.route('/classify', methods=['GET', 'POST'])
def classify():
    query= request.json['query']
    url = request.json['url']
    print query, url
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
    # for x in range(len(sims)):
    #     sims[x] = (((len(sims)-x)*.1)+1)*sims[x]
    # for x in tags[:5]:
    #     # print x
    #     # v = x+'.n.01'
    #     # print v
    #     try:
    #         s = wn.synsets(x)[0]
    #         # print s
    #         sims.append(query.path_similarity(s))
    #     except:
    #         print "COULDNT SIMS: " + str(x)
    sims = [x for x in sims if x != None]
    print sims

  

    print sims

    print "SCORE: " + str(sum(sims)/float(len(sims)))
    if len(sims) == 0:
        return str(-1)
    return str(sum(sims)/float(len(sims)))


    

@app.route('/', methods=['GET'])
def static_index():
    return render_template("index.html")


# import threading

# class ModelDownloader(threading.Thread):

#   def __init__(self, objs):
#     threading.Thread.__init__(self)
#     self.objs = objs

#   def run(self):
#     import warehouse_scraper as w
#     import requests
#     import urllib
#     import json
#     for o in self.objs:
#       datum = w.find(o)[0]["description"]["binaries"]
#       print json.dumps(datum, indent=2)
#       id = ""
#       if "s7" in datum:
#         id = datum["s7"]["id"]
#       elif "s8" in datum:
#         id = datum["s8"]["id"]
#       elif "s6" in datum:
#         id = datum["s6"]["id"]
#       else:
#         print "NO SKP FILE FOUND"
#         return

#       url = "https://3dwarehouse.sketchup.com/warehouse/getpubliccontent?contentId=" + id + "&fn=" + o + ".skp"
#       print url


#       urllib.urlretrieve(url, "data/" + o + ".skp")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, ssl_context=("/Users/lee/pennapps2015/NLP/server.crt", "/Users/lee/pennapps2015/NLP/server.key"))

#     ModelDownloader(["banana"]).run()


