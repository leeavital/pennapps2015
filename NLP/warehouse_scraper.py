import requests
import json
import shutil

filetypes = ["ks", "k2", "bot_st"]
# could also be any of:
# skj, smontage, ks, bot_smontage, st, s8, lt, bot_st, log

def log(message):
    requests.get("http://datarelayer.appspot.com/set/error/" + message)
    print "error: ", message

def find(query):
    # returns a list of strings to drop into grab
    r = requests.get("https://3dwarehouse.sketchup.com/warehouse/Search",
                     params = {"class":"entity","q":query,"startRow":"1",
                               "endRow":"100"})
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
                "https://3dwarehouse.sketchup.com/warehouse/GetEntity",
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

def objCNNscore(obj, query):
    return float(requests.post('http://158.130.167.232/classify',
                               json = {'url':obj["description"]["binaries"]["bot_lt"]["url"],
                                       'query':query}).text)

def select(find_results, query):
    scores = []
    for result in find_results:
        scores.append(objCNNscore(result, query))
    return find_results[scores.index(max(scores))]

if __name__ == '__main__':
    print 'Model: '
    query = str(raw_input())
    print select(find(query), query)
