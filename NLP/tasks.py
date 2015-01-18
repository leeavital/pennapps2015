import os
import os.path
import urllib
import zipfile
import requests
from celery import Celery

app = Celery('hello', broker='redis://104.236.92.111:6379/0')

CLASSIFY_ENDPOINT = 'http://158.130.167.232/classify'
LOCAL_IP = urllib.urlopen('http://ipecho.net/plain').read()

def grab(entity):
    entity_id = entity['id']
    query = entity['query']
    binary_url = entity['binary_url']
    filename = 'warehouse-'+query+'-'+entity_id+'.'+binary_url.split('name=')[1].split('&')[0]+'.zip'
    urllib.urlretrieve(binary_url, filename)
    model_path = None
    with zipfile.ZipFile(filename) as zf:
        for member in zf.infolist():
            words = member.filename.split('/')
            path = filename.replace('.zip', '')
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''):
                    continue
                path = os.path.join(path, word)
            if '.kml' not in member:
                zf.extract(member, path)
                if '.dae' in member:
                    model_path = path
    return model_path

@app.task
def processor(particle):
    query, entry_id = particle
    entity = None
    try:
        r = requests.get(
            "https://3dwarehouse.sketchup.com/warehouse/GetEntity",
            params = {"id":entry_id}).json()
        for filetype in ["ks", "k2"]:
            if filetype in r["binaries"]:
                if r["binaries"][filetype]["fileSize"] < 15000000:
                    entity = r
                    binary_url = r["binaries"][filetype]["url"]
                    entity["binary_url"] = binary_url
                    entity["query"] = query
    except:
        log("warehouse-processor-"+entry_id)
        return None
    if entity == None:
        return None
    if entity['description']['reviewCount'] >= 1 and entity['description']['averageRating'] <= 2:
        return None
    try:
        r = requests.post(CLASSIFY_ENDPOINT, json = {'url':obj['description']['binaries']['bot_lt']['url'],
                                                     'query':query})
        score = float(r.text)
    except:
        log("warehouse-processor-"+str(particle))
        return None
    entity["score"] = score
    model_path = grab(entity)
    entity["model_path"] = model_path
    ## PROBABLY NOT GOING TO WORK
    entity["url_on_child"] = 'http://' + LOCAL_IP + model_path



