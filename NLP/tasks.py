import os
import os.path
import json
import urllib
import urllib2
import zipfile
import requests
from celery import Celery

app = Celery('hello', broker='redis://104.236.92.111:6379/0')



CLASSIFY_ENDPOINT = 'http://104.236.90.178/classify'
COLLECTOR_ENDPOINT = 'http://104.236.95.94:8090/'
LOCAL_IP = urllib.urlopen('http://ipecho.net/plain').read()


def log(message):
    requests.post(COLLECTOR_ENDPOINT, data=json.dumps({"query":message}), headers={'content-type':'application/json'})
    print "error: ", message

def grab(entity):
    entity_id = entity['id']
    query = entity['query']
    binary_url = entity['binary_url']
    filename = 'warehouse-'+query+'-'+entity_id+'.'+binary_url.split('name=')[1].split('&')[0]+'.zip'
    urllib.urlretrieve(binary_url, filename)
    model_path = None
    model_filename = None
    with zipfile.ZipFile(filename) as zf:
        for member in zf.infolist():
            words = member.filename.split('/')
            path = 'models/'+filename.replace('.zip', '')
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''):
                    continue
                path = os.path.join(path, word)
            if '.kml' not in member.filename:
                zf.extract(member, path)
                if '.dae' in member.filename:
                    model_path = path
                    model_filename = member.filename
    return model_path, model_filename

@app.task
def processor(particle):
    query, entry_id = particle
    entity = None
    try:
        r = json.load(urllib2.urlopen(
            'https://3dwarehouse.sketchup.com/warehouse/GetEntity?id='+entry_id
            ))
        for filetype in ["ks", "k2"]:
            if filetype in r["binaries"]:
                if r["binaries"][filetype]["fileSize"] < 15000000:
                    entity = r
                    binary_url = r["binaries"][filetype]["url"]
                    entity["binary_url"] = binary_url
                    entity["query"] = query
    except:
        log("warehouse-processor1-"+entry_id)
        return False
    if entity == None:
        log("warehouse-processor2-"+entry_id)
        return False
    if entity['reviewCount'] >= 1 and entity['averageRating'] <= 2:
        log("warehouse-processor3-"+entry_id)
        return False
    try:
        print entity['binaries']['bot_lt']['url']
        #r = requests.post(CLASSIFY_ENDPOINT)
        js = {'url':entity['binaries']['bot_lt']['url'],'query':query}
        print "GOT JS"
        import json
        r = requests.post(CLASSIFY_ENDPOINT, data = json.dumps(js), headers={'content-type':'application/json'})
        score = float(r.text)
    except:
        log("warehouse-processor4-"+str(particle))
        return False
    try:
        creation = {}
        creation["cnn_score"] = score
        print "A"
        model_path, model_filename = grab(entity)
        print "A.5"
        creation["model_path"] = model_path + '/' + model_filename
        print "A.6"
        #print 'xvfb-run meshlabserver -l '+model_path+'/logfile.txt -i ' + creation['model_path'] + ' -s measure.mlx'
        #os.system('xvfb-run meshlabserver -l '+model_path+'/logfile.txt -i ' +
        #          creation['model_path'] + ' -s measure.mlx')
        print "B"
        #with open(model_path + '/logfile.txt') as logfile:
        #    creation["mesh"] = logfile.read()
        print "C"
        creation["url_on_child"] = 'http://' + LOCAL_IP + '/' + model_path
        print "SENDING LAST"
        requests.post(COLLECTOR_ENDPOINT, data = json.dumps(creation),headers={'content-type':'application/json'})
    except:
        log("warehouse-processor5-"+str(particle))
        return False
    return True
