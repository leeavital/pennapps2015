import requests
import xml.dom.minidom as DOM
import urllib

def search(q):

  url = "http://archive3d.net/?tag=" + q

  txt = requests.get(url).text

  xml = DOM.parseString(txt)

  anchors = xml.getElementsByTagName("a")

  downloadAnchors = filter(lambda a: "download" in a.getAttribute("href"), anchors)
  downloadLinks = map(lambda a: a.getAttribute("href"), downloadAnchors)

  for link in downloadLinks:
    offset = link.index("id=") + 3 
    dl = "http://archive3d.net/?a=download&do=get&id=" + link[offset:]
    print dl

    urllib.urlretrieve(dl, link[offset:] + ".zip")





search("dog")
