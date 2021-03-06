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
app = Flask(__name__)
app.config.from_object(__name__)

MASTER_SERVER_ENDPOINT  = "http://104.236.95.94:8090/model/"

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

pp = pprint.PrettyPrinter(indent=4)

SCENE_FILE = "../Descriptions/first_demo.txt"
server = jsonrpc.ServerProxy(jsonrpc.JsonRpc20(),
        jsonrpc.TransportTcpIp(addr=("127.0.0.1", 8080)))

WAITING = "waiting"
DOWNLOADING = "downloading"
READY = "ready"
server_state = "waiting"


f = {}
# scenes = [f for f in open(SCENE_FILE).read().split('\n') if f != '']
@app.route('/', methods=['POST'])
def get_entities():
    global server_state
    if server_state == WAITING or server_state == READY:
      print "Downloading..."
      server_state = DOWNLOADING
    else:
      print "not accepting queries right now"
      return jsonify({"error":"busy"})
    print 'here'
    global f
    scene = request.json['text']
    scene = "There is an outside.  There is a player.  " + scene
    scene = re.sub(' out', ' outside ', scene)
    scene = re.sub(' me', ' the player ', scene)

    print scene
    print "\n"
    result = loads(server.parse(scene))
    print "got something from corenlp"
    entities = {}
    deps = []
    corefs = []
    if 'coref' in result:
        # pp.pprint(result['coref'][0][0]) 
        corefs = result['coref'][0]
    for sent in result['sentences']:
        print "sentent ", sent
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
            elif 'advmod' in dep[0]:
                entities['environment'] = dep[1]

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
    print "got here"
    f = {}
    pp.pprint(entities)
    print "\n"
    pp.pprint(deps)
    print "\n"
    f['entities'] = entities
    f['deps'] = deps
    # kick off an entity parse job
    ModelDownloader(entities).start()
    return jsonify(f)


@app.route('/latest', methods=['POST', 'GET'])
def get_latest():
  if server_state == READY:
    return jsonify(f)
  else:
    return jsonify({"error": "not ready"})


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


import threading


class ModelDownloader(threading.Thread):

  def __init__(self, entities):
    threading.Thread.__init__(self)
    self.entities = entities
    self.RESOURCE_PATH = "/Users/lee/lolzunity/Assets/Resources/"

  def run(self):
    import time
    import urllib
    from zipfile import ZipFile
    import glob
    import requests
    import os
    entityToModel = {}
    try:
      for e in self.entities:
        global server_state
        print "downloading a entity...", e
        # get a real link
        # zipPath = "http://104.131.24.156/NLP/warehouse-cat-fa44223c6f785c60e71da2487cb2ee5b.k2.zip"
        zipPath = requests.get(MASTER_SERVER_ENDPOINT + e).text
        print zipPath
        zipDestination = self.RESOURCE_PATH + e + ".zip"
        print zipDestination
        urllib.urlretrieve(zipPath,zipDestination)
        os.chmod(zipDestination, 777)
        ZipFile(zipDestination).extractall(self.RESOURCE_PATH + e)
        daeSansExtension = (glob.glob(self.RESOURCE_PATH + e + "/**/*.dae")[0])[0:-4]
        entityToModel[e] = daeSansExtension.replace(self.RESOURCE_PATH, '')
        # do real work

      print entityToModel
      global f
      f["entityModels"] = entityToModel
      server_state =  READY
    except:
      server_state = WAITING

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
