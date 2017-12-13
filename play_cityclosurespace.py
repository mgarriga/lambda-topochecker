# -*- coding: utf-8 -*-

from spacegraph import *
# from matcher.acexp import *
# from matcher.bigformula import *
# from helpers.helpers import *
# from helpers.aria_log import lg, DEBUG
from pprint import pprint
# from helpers.random_bigraphs import *
# from matcher.match2 import match_iso
# from ks.ks2 import *
# from IPython import embed
# from city_loader import *
# from ks.loader import *
import glob
import time



# https://stackoverflow.com/questions/41651134/cant-run-binary-from-within-python-aws-lambda-function

# http://www.perrygeo.com/running-python-with-compiled-code-on-aws-lambda.html

# https://stackoverflow.com/questions/42301357/aws-lambda-using-executable-with-python

# https://stackoverflow.com/questions/41651134/cant-run-binary-from-within-python-aws-lambda-function




# https://github.com/ellson/MOTHBALLED-graphviz/issues/1271

# https://lifeinplaintextblog.wordpress.com/deploying-graphviz-on-aws-lambda/
# https://github.com/restruct/dot-static
# https://stackoverflow.com/questions/40528048/pip-install-pygraphviz-no-package-libcgraph-found
# http://www.perrygeo.com/running-python-with-compiled-code-on-aws-lambda.html





# city = import_timo_city("../chinadataplay/network-bigraph.gml")

spatialprop = " (N [TRANSPORTBUSSTOP])"
# spatialprop = " (N [dm])"
# spatialprop = " (N [taxi])"

# # space = SpacePredicatedGraph(city) # from bigraph. note: closure space will be bigraphical
# from closure file
start_time = time.time()

# space = SpacePredicatedGraph(closurefile="../chinadataplay/networks_generated/full-network-trajects10300searchrange10bglimitpresences1poicount11741-closurespace.gml")
space = SpacePredicatedGraph(closurefile="../chinadataplay/networks_generated/full-network-trajects10357searchrange20bglimitpresences1poicount11741-closurespace.gml")
# space = SpacePredicatedGraph(closurefile="../chinadataplay/mini-closurespace.gml")

# space = SpacePredicatedGraph(closurefile='../chinadataplay/networks_generated/full-network-ROMA-searchrange10-closurespace.gml')

# space.dot_debug("mini")

end_time = time.time()
print 'loading took', "{0:.2f}".format(end_time - start_time), "sec"

start_time = time.time()


# NOT FINALLY ( (r in l1) AND NEXT (FINALLY((r in l1) AND NEXT (FINALLY( (r in l1))))))

spatialprop="R([taxi],[TRANSPORTBUSSTOP],[TRANSPORTSUBWAY]) & (N [TRANSPORTFUEL])"
# spatialprop="R([taxi],([TRANSPORTSUBWAY] | [TRANSPORTBUSSTOP]),[FOODBAR]) "

spatialprop="R([taxi],([TRANSPORTSUBWAY] | [TRANSPORTBUSSTOP]),[FOODBAR]) & (N [TRANSPORTFUEL]) "

print 'clpoints satisfying spatialprop', len(space.invoke_topochecker(spatialprop=spatialprop))
end_time = time.time()
print 'topo invoke took', "{0:.2f}".format(end_time - start_time), "sec"

print 'nodes',len(space),'edges',space.number_of_edges()
# print 'formula fragment',city.formula[:200],'...'

# print 'city.size',city.size


# space.invoke_topochecker(spatialprop="R([taxi],[TRANSPORTBUSSTOP],[TRANSPORTSUBWAY]) & (N N [TRANSPORTFUEL])")




# space = SpacePredicatedGraph(closurefile="../chinadataplay/1-closurespace.gml")
# space.dot_debug("1")
# space = SpacePredicatedGraph(closurefile="../chinadataplay/2-closurespace.gml")
# space.dot_debug("2")



# embed()