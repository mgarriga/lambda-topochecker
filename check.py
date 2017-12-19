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


# space = SpacePredicatedGraph(closurefile="../chinadataplay/networks_generated/full-network-trajects10357searchrange20bglimitpresences1poicount11741-closurespace.gml")
copyfile("./mini-closurespace.gml", "/tmp/mini-closurespace.gml")
copyfile("./topochecker", "/tmp/topochecker")
if not os.path.isdir('/tmp/topotmp'):
    copytree("./topotmp","/tmp/topotmp")

#space = SpacePredicatedGraph(closurefile="./mini-closurespace.gml")
space = SpacePredicatedGraph(closurefile="/tmp/mini-closurespace.gml")

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
# space = unpickle_clspace("clspace.pickle")

class Checker(Resource):
    def get(self, spatialprop):
        start_time = time.time()

        global space

        #LOCAL
        #current_space = json.load(urllib2.urlopen("http://localhost:5001/space"))
        #current_space = json.load(urllib2.urlopen("http://10.79.11.36:5001/space"))

        #EC2 Server
        current_space = json.load(urllib2.urlopen("http://52.27.220.158:5001/space"))
        #print 'got taxi positions',len(current_space),
        # populate with current space
        space.populate_closurespace_presence_map(current_space)
        #print 'clpoints satisfying spatialprop', len(space.invoke_topochecker(spatialprop=spatialprop)),
        print spatialprop
        result = {'data': len(space.invoke_topochecker(spatialprop=spatialprop))}
        end_time = time.time()
        #print 'eval took', "{0:.2f}".format(end_time - start_time), "sec"
        return result

app = Flask(__name__)
api = Api(app)
api.add_resource(Checker, '/check/<string:spatialprop>')

class HealthCheck(Resource):
    def get(self):
        return {'status':'up'}

api.add_resource(HealthCheck, '/check')


if __name__ == '__main__':
    # spatialprop = " (N [TRANSPORTBUSSTOP])"
    # print 'clpoints satisfying spatialprop', len(space.invoke_topochecker(spatialprop=spatialprop))

    # or through the api:
    # http://localhost:5000/check/(N%20[TRANSPORTBUSSTOP])

    # REMOTE
     app.run(host='0.0.0.0')
