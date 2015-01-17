import requests
import json
import shutil
import urllib
import zipfile
import os.path

CLASSIFY_ENDPOINT = 'http://158.130.167.232/classify'

# PREFILTER ARGUMENTS
filetypes = ["ks", "k2"]


# POSTFILTER ARGUMENTS



def log(message):
    requests.get("http://datarelayer.appspot.com/set/error/" + message)
    print "error: ", message

def find(query, num = 30):
    # returns a list of strings to drop into grab
    r = requests.get("http://3dwarehouse.sketchup.com/warehouse/Search",
                     params = {"class":"entity","q":query,"startRow":"1",
                               "endRow":str(num)})
    output = []
    try:
        entries = r.json()["entries"]
    except:
        log("warehouse-search-"+query)
        return []
    for entry in entries:
        entry_id = entry["id"]
        try:
            entity = requests.get(
                "https://3dwarehouse.sketchup.com/warehouse/GetEntity",
                params = {"id":entry_id}).json()
            for filetype in filetypes:
                if filetype in entity["binaries"]:
                    if entity["binaries"][filetype]["fileSize"] < 15000000:
                        output.append({"source":"warehouse",
                                       "url":entity["binaries"][filetype]["url"],
                                       "description":entity})
                        break
        except:
            log("warehouse-entity-"+entry_id)
            return []
    return output

def preFilter(objs, query):
    staj = []
    for obj in objs:
        if obj['description']['reviewCount'] < 1 or obj['description']['averageRating'] > 2:
            staj.append(obj)
    objs = staj
    try:
        scores = objsCNNscore(objs, query)
    except:
        log("warehouse-cnn-"+query)
        return []
    staj = zip(scores, objs)
    objs = sorted(staj, key = lambda x: x[0])
    objs.reverse() # sorted from highest to lowest
    objs = map(lambda x:x[1], objs[:max([int(len(objs)/3.0), 3]):-1])
    return objs

def postFilter(objs):
    # must be run only after all the objs have been downloaded and objs store
    # the way they were downloaded
    # must convert to standard file format first
    # once we do this then we can do any interesting postfiltering
    # but we probably want to pass some stuff over to this from the prefilter ;)
    return objs

def grab(obj, query, filename = None):
    if filename == None:
        filename = 'warehouse-'+query+'-'+obj['description']['id']+'.'+obj['url'].split('name=')[1].split('&')[0]+'.zip'
    urllib.urlretrieve(obj['url'], filename)
    model_path = None
    with zipfile.ZipFile(filename) as zf:
        for member in zf.infolist():
            print member
            words = member.filename.split('/')
            path = filename.replace('.zip','')
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''):continue
                path = os.path.join(path, word)
            if '.kml' not in member:
                zf.extract(member, path)
                if '.dae' in member:
                    model_path = path
    return model_path

def objsCNNscore(objs, query):
    # use urllib and do this asynchronously when we have time
    return map(lambda x:objCNNscore(x, query), objs)
    '''
# grequests is broken on python 2.7
    grobjs = [grequests.post(CLASSIFY_ENDPOINT, json = {'url':obj['description']['binaries']['bot_lt']['url'],
            'query':query, 'tags':obj['description']['tags']}) for obj in objs]
    return map(lambda x:float(x.text), grequests.map(grobjs))
    '''


def objCNNscore(obj, query):
    return float(requests.post(CLASSIFY_ENDPOINT,
                               json = {'url':obj['description']['binaries']['bot_lt']['url'],
                                       'query':query}).text)



if __name__ == '__main__':
    print 'Model: '
    query = str(raw_input())
    print preFilter(find(query, 10))
