import requests
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


####
'''

root -> children -> local

root gets list of possible entitites, sends them out to children
children operate on possible entities, and send back good processed stuff to root
root does the reduce step on what the children send it
the root now knows what model to use, and so gives the client the URL on one of the children pointing to the model


'''
####



def log(message):
    requests.get("http://datarelayer.appspot.com/set/error/" + message)
    print "error: ", message


def find(query):
    print "QUERY: " + str(query)
    # returns a list of strings to drop into grab
    r = requests.get("http://3dwarehouse.sketchup.com/warehouse/Search",
                     params={"class":"entity","q":query,"startRow":"1", "endRow":"10"})

    output = []
    try:
        entries = r.json()["entries"]
    except:
        log("warehouse-search-"+query)
        return
    for entry in entries:
        entry_id = entry["id"]
        try:
            entity = requests.get(
                "http://3dwarehouse.sketchup.com/warehouse/GetEntity",
                params = {"id":entry_id}).json()
            for filetype in filetypes:
                if filetype in entity["binaries"]:
                    if entity["binaries"][filetype]["fileSize"] < 15000000:
                        output.append({"source":"warehouse",
                                       "url":entity["binaries"][filetype]["url"],
                                       "description":entity})
        except:
            log("warehouse-entity-"+entry_id)
    return output

'''
def grab(obj, filename):
    r = requests.get(obj["url"])
    with open(filename, 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)
'''


@app.route('/', methods=['POST'])
def collect():
    print request
    entity = request.get_json()
    print entity
    print entity['cnn_score']
    return 'yo homilimlilimi'

def collector(entities):
    score_sorted = sorted(entities, key = lambda x: x['score'])
    best_entity = entities[-1]
    return best_entity["url_on_child"]

if __name__ == '__main__':
    print 'Model: '
    query = str(raw_input())
    for particle in emitter(query):
        processor.delay(particle)
    app.run(host='0.0.0.0', port=80)
