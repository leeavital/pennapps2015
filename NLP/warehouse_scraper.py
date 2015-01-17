import requests
import json
import shutil

filetypes = ["ks", "k2"]
# could also be any of:
# skj, smontage, ks, bot_smontage, st, s8, lt, bot_st, log

def logError(message):
    requests.get("http://datarelayer.appspot.com/set/error/" + message)
    print "error: ", message

def find(search):
    # returns a list of strings to drop into grab
    r = requests.get("https://3dwarehouse.sketchup.com/warehouse/Search",
                     params = {"class":"entity","q":search,"startRow":"1",
                               "endRow":"1"})
    output = []
    try:
        entries = r.json()["entries"]
    except:
        logError("3dwarehouse-search-"+search)
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
                        output.append({"source":"3dwarehouse",
                                       "url":entity["binaries"][filetype]["url"],
                                       "description":entity})
        except:
            logError("3dwarehouse-entity-"+entry_id)
    return output

def grab(obj, filename):
    r = requests.get(obj["url"])
    with open(filename, 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)



