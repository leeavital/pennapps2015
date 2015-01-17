import jsonrpc
import pprint
from simplejson import loads

pp = pprint.PrettyPrinter(indent=4)

SCENE_FILE = "../Descriptions/basic_scenes.txt"
server = jsonrpc.ServerProxy(jsonrpc.JsonRpc20(),
                             jsonrpc.TransportTcpIp(addr=("127.0.0.1", 8080)))


scenes = [f for f in open(SCENE_FILE).read().split('\n') if f != '']
for scene in scenes:
	result = loads(server.parse(scene))
	entities = {}
	# pp.pprint(result)
	for sent in result['sentences']:
		# pp.pprint(sent['dependencies'])
		for dep in sent['dependencies']:
			if dep[0] == 'det':
				entities[dep[1]] = []
			if dep[0] == 'amod':
				entities[dep[1]] = dep[2]

	print scene
	print entities