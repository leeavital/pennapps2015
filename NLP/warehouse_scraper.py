import requests
import pickle
import glob
import json
import shutil
import urllib
import zipfile
import os.path
from tasks import processor
from flask import Flask, request, redirect, url_for, \
     abort, render_template, flash, make_response, jsonify # clean these up
app = Flask(__name__)
app.config.from_object(__name__)

CLASSIFY_ENDPOINT = 'http://158.130.167.232/classify'
LOCAL_IP = urllib.urlopen('http://ipecho.net/plain').read()


'''

root -> children -> local

root gets list of possible entitites, sends them out to children
children operate on possible entities, and send back good processed stuff to root
root does the reduce step on what the children send it
the root now knows what model to use, and so gives the client the URL on one of the children pointing to the model


'''



def log(message):
    requests.get("http://datarelayer.appspot.com/set/error/" + message)
    print "error: ", message


def emitter(query):
    # returns a list of strings to drop into grab
    r = requests.get("http://3dwarehouse.sketchup.com/warehouse/Search",
                     params = {"class":"entity","q":query,"startRow":"1",
                               "endRow":"5"})
    output = []
    try:
        entries = r.json()["entries"]
    except:
        log("warehouse-emitter1-"+query)
        return []
    r = requests.get("http://3dwarehouse.sketchup.com/warehouse/Search",
                     params = {"class":"entity","q":query,"startRow":"1",
                               "endRow":"5","sortBy":"popularity DESC"})
    try:
        entries += r.json()["entries"]
    except:
        log("warehouse-emitter2-"+query)
        return []
    return zip([query] * len(entries), map(lambda x:x["id"], entries))
@app.route('/model/<query>',methods=['POST', 'GET'])
def get_model(query):
    if "CACHES/"+query+".pkl" in glob.glob("CACHES/*"):
        fl =  open("CACHES/"+str(query)+'.pkl', 'r')
        jsons = pickle.loads(fl.read())
        print jsons
        fl.close()
        if len(jsons) < 5:
            return "NO_PATH"
        jsons = sorted(jsons, key=lambda x: x['cnn_score'], reverse=True)
        print jsons
        d = jsons[0]
    
        return str(d['url_on_child'][:-3] + '/NLP'+d['model_path'][2:])
    print "HERE"
    requests.get('http://104.236.95.94:8090/add/'+str(query))
    return "NO_PATH"
@app.route('/', methods=['POST', 'GET'])
def collect():
    entity = request.get_json()
    query = entity['model_path'].split('-')[1]
    fl =  open("CACHES/"+str(query)+'.pkl', 'rw')
    f = pickle.loads(fl.read())
    fl.close()
    fl =  open("CACHES/"+str(query)+'.pkl', 'w')
    f.append(entity)
    p = pickle.dumps(f)
    fl.write(p)
    fl.close()
    return 'Added'

def collector(entities):
    score_sorted = sorted(entities, key = lambda x: x['score'])
    best_entity = entities[-1]
    return best_entity["url_on_child"]

@app.route('/add/<model>', methods=['GET', 'POST'])
def add_model(model):
    print glob.glob('CACHES/*')
    if 'CACHES/'+model+'.pkl' in glob.glob('CACHES/*'):
        return "Already in cache"
    else:
	f = []
	fl = open("CACHES/"+str(model)+'.pkl', 'w')
	fl.write(pickle.dumps(f))
	fl.close()
        for particle in emitter(model):
           processor.delay(particle)
    return "Added"

if __name__ == '__main__':
    count = 0
    #query = str(raw_input())
    #t = time.time()
    #for particle in emitter(query):
    #    processor.delay(particle)
    #	count += 1
    app.run(host='0.0.0.0', port=8090)
