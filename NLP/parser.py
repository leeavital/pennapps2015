import jsonrpc
import pprint
from simplejson import loads

pp = pprint.PrettyPrinter(indent=4)

SCENE_FILE = "../Descriptions/basic_scenes.txt"
server = jsonrpc.ServerProxy(jsonrpc.JsonRpc20(),
                             jsonrpc.TransportTcpIp(addr=("127.0.0.1", 8080)))


scenes = [f for f in open(SCENE_FILE).read().split('\n') if f != '']
for scene in scenes[:-1]:
    print scene
    print "\n"
    result = loads(server.parse(scene))
    entities = {}
    deps = []
    corefs = []
    if 'coref' in result:
        # pp.pprint(result['coref'][0][0]) 
        corefs = result['coref'][0]
    for sent in result['sentences']:
        # pp.pprint(sent['dependencies'])
        for dep in sent['dependencies']:
            if dep[0] == 'det':
                entities[dep[1]] = []
            elif dep[0] == 'amod' or dep[0] == 'nsubj':
                if 'is' not in dep:
                    if dep[1] in entities:
                        entities[dep[1]].append(dep[2])
                    elif dep[2] in entities:
                        entities[dep[2]].append(dep[1])

            elif 'prep_' in dep[0]:
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
                            name = [z for z in obj2[0].split() if z in entities]
                            deps.append([dep[1], dep[0], name])
                            # deps.append([obj2[0], dep[0], dep[1]])
                        elif dep[2] in obj2[0]:
                            name = [z for z in obj2[0].split() if z in entities]

                            deps.append([dep[1], dep[0], name])

                            # deps.append([obj1[0], dep[0], dep[1]])

    # deps = set(deps)
    pp.pprint(entities)
    print "\n"
    pp.pprint(deps)
    print "\n"