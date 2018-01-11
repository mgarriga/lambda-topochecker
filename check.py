from spacegraph import *

from shutil import copyfile, copytree
from flask import Flask, request
from flask_restful import Resource, Api
import os
import time
import json
import urllib2
try:
    import cPickle as pickle
except:
    import pickle
import json
try:
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop
    tornado_imported = True
except ImportError:
    tornado_imported=False


# space = SpacePredicatedGraph(closurefile="../chinadataplay/networks_generated/full-network-trajects10357searchrange20bglimitpresences1poicount11741-closurespace.gml")
# space = SpacePredicatedGraph(closurefile="./mini-closurespace.gml")
# space = SpacePredicatedGraph(closurefile="full4mouseia-closurespace.gml")
# space = SpacePredicatedGraph(closurefile="full4mouseia-closurespace-d10.gml")
# space = SpacePredicatedGraph(closurefile="full4mouseia-closurespace-d5.gml")


config = json.load(open('config_setup.json'))

#Copying to tmp to run in lambda because you can only write on TMP
copyfile("./topochecker", "/tmp/topochecker")
copyfile("./clspace.pickle", "/tmp/clspace.pickle")
if not os.path.isdir('/tmp/topotmp'):
    copytree("./topotmp","/tmp/topotmp")

def pickle_clspace(clspace, filename):
    copyfile(filename,"/tmp/" + filename)
    with open("/tmp/" + filename, 'wb') as output:
        pickle.dump(clspace, output, pickle.HIGHEST_PROTOCOL)


def unpickle_clspace(filename):
    print "Loading clspace from", filename + "..."
    with open(filename, 'rb') as input:
        clspace = pickle.load(input)
    return clspace

# pickle_clspace(space,"clspace.pickle")
space = unpickle_clspace("/tmp/clspace.pickle")

print 'Loaded closurespace: points', len(space),'edges', space.number_of_edges()

class Checker(Resource):
    def get(self, spatialprop):
        start_time = time.time()
        global space
        current_space = json.load(urllib2.urlopen(config['state_keeper_serverport']+"/space"))
        print 'got taxi positions',len(current_space),
        # populate with current space
        space.populate_closurespace_presence_map(current_space)
        print 'clpoints satisfying spatialprop', len(space.invoke_topochecker(spatialprop=spatialprop)),
        result = {'data': len(space.invoke_topochecker(spatialprop=spatialprop))}
        end_time = time.time()
        print 'eval took', "{0:.2f}".format(end_time - start_time), "sec"
        return result

app = Flask(__name__)
api = Api(app)
api.add_resource(Checker, '/check/<string:spatialprop>')

class HealthCheck(Resource):
    def get(self):
        return {'status':'up'}

api.add_resource(HealthCheck, '/check')


if __name__ == '__main__':

    if tornado_imported:
        print 'Spawning tornado.'

        server = HTTPServer(WSGIContainer(app))
        server.bind(5000)
        server.start(4)
        IOLoop.current().start()
    else:
        print 'Spawning flask'
        app.run(host= '0.0.0.0',port=5000)
