#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
topoinvoker
"""
from networkx import Graph, DiGraph, strongly_connected_component_subgraphs, draw, relabel_nodes, isolates
from networkx.drawing.nx_agraph import to_agraph
from networkx import write_gml, read_gml
import uuid
import os
from pprint import pprint
import errno
import subprocess
import re
import time

imported_graphviz = False

# DEBUG_INVOKER = True
DEBUG_INVOKER = False


class TopocheckerException(Exception):
    """ class producing relevant input files and invoking topochecker with a property"""

    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(TopocheckerException, self).__init__(message)
        self.message = message
        print "topochecker returned with non-zero status. Stdout output:\n", message
        print 'output was:'
        print message.output


class SpacePredicatedGraph(DiGraph):
    """ graph structure to hold propositions on points of space. built from a bigraph."""

    def __init__(self, bg=False, closurefile=False, nxclosurespace=None):
        DiGraph.__init__(self)

        self.predicates = {}
        self.reversed = None
        self.atoms = set([])
        # keep the edges we added to make the graph symmetric
        self.symmetric_edges = list()
        self.marked = set()

        # dict holding relabellings -- topochecker expects ordered [0..] in dot
        # and csv vals
        self.topochecker_relabelling = {}

        if bg:
            self.from_bg(bg)
            self.make_symmetric()
        elif closurefile:
            self.read_gml(closurefile)
        elif nxclosurespace:
            # add all nodes and attrs from nxclosurespace
            for n in nxclosurespace.nodes():
                for p in nxclosurespace.node[n]['predicates']:
                    self.add_predicate(p=p, n=n)
            self.add_edges_from(nxclosurespace.edges(data=True))
            # raise NotImplemented()

        self.default_topostatements = [
            "Let reach(x,y) = !((!y)S(!x));", "Let R(a,b,e) = a & !((!( (b & !((!e)S(!(b|e)))) & (b & !((!a)S(!(b|a)))) ))S(!(a|( (b & !((!e)S(!(b|e)))) & (b & !((!a)S(!(b|a)))) ))));"]

        # make sure topochecker is there. otherwise raise exception
        # self.g = g # SpacePredicatedGraph instance
        self.path_to_executable = "./topochecker"

        # use tmpfs on linux to be faster
        # self.tmppath = "/dev/shm/topotmp/"
        self.tmppath = "./topotmp/"

        # make sure the directory exists
        try:
            os.makedirs(self.tmppath)
        except OSError:
            if not os.path.isdir(self.tmppath):
                raise

        self.remove_isolates()
                
    def has_predicate(self, n, p):
        for term in self.predicates[n]:
            if term == p:
                return True
        return False

    def add_predicate(self, n, p):
        ''' adds predicate p to node n'''
        newp = p
        if not n in self:
            self.add_node(n)
        try:
            if not self.has_predicate(n, newp):
                self.predicates[n].append(newp)
        except KeyError:    # n has no predicate yet
            self.predicates[n] = [newp]

    def make_symmetric(self):
        """ make all relations in SpacePredicatedGraph symmetric """
        for start, target in self.edges():
            self.symmetric_edges.append(tuple([target, start]))
            self.add_edge(target, start)

    def from_bg(self, bg):
        """ Build SpacePredicatedGraph from a bigraph.
        Add fake container node to put children in for closure to work as it does in link structure.
        """
        g = bg.graph_repr
        for n in g.nodes_iter(data=True):
            node_id = n[0]
            ports = n[1].get("links", [])
            self.add_node(node_id, label=n[1]["control"])
            self.add_predicate(node_id, node_id)
            self.add_predicate(node_id, n[1]["control"])
            if g.successors(n[0]):
                # adding container node to put children in for closure to
                # work as it does in link structure
                self.add_node("cont" + node_id, label="cont" + node_id)
                # self.predicates["cont"+node_id]=""
                self.add_predicate("cont" + node_id, "container")
                self.add_edge(node_id, "cont" + node_id)
                children = g.successors(n[0])
                for child_id in children:
                    self.add_edge("cont" + node_id, child_id)

            for port in ports:
                self.add_node(port, label=port)
                self.add_predicate(port, port)
                self.add_predicate(port, "portname")
                self.add_edge(node_id, port)

    def export_gml(self, filename):
        """ export as GML file"""
        write_gml(self, filename + '-SpacePredicatedGraph.gml')

    def read_gml(self, filename):
        """ read and init from GML. """
        print 'Loading gml from', filename
        a = read_gml(filename)
        for n in a.nodes():
            for p in a.node[n]['predicates']:
                self.add_predicate(p=p, n=n)
        self.add_edges_from(a.edges(data=True))

    def relabel(self, restore=False):
        """ relabel nodes for outputting to topochecker. do it in place for efficiency.
        if restore is True, restore the labelling back """
        if restore:
            self = relabel_nodes(
                self, self.topochecker_relabelling_inverse, copy=False)
            return
        if not self.topochecker_relabelling:
            self.topochecker_relabelling = dict(
                zip(self.nodes(), range(0, len(self))))
            self.topochecker_relabelling_inverse = dict(
                (v, k) for k, v in self.topochecker_relabelling.iteritems())
        self = relabel_nodes(self, self.topochecker_relabelling, copy=False)

    def to_dot(self):
        """ write dot, no positioning info, efficient"""
        self.relabel()
        if imported_graphviz:
            A = to_agraph(self)
            dotstring = A.to_string()
        else:
            # without the graphviz dependancies:
            dotstring = 'strict digraph  {'
            for src, dest in self.edges():
                src + dest
                dotstring += "%s ->  %s;" % (src, dest)
            dotstring += '}'
        # must relabel nodes before outputting to dot
        self.relabel(restore=True)
        return dotstring

    def remove_isolates(self):
        """ workaround for bug in topochecker: topochecker will fail if there are evaluation 
        declarations of closure points that are not found in the spacemodel."""
        isolate_nodes = list(isolates(self))
        if isolate_nodes:
            print 'removing isolate closure points', isolate_nodes
            self.remove_nodes_from(isolate_nodes)

    def topo_csv(self):
        """ build csv propositions for topochecker"""
        # nodes must be labelled from 0
        line = []
        lines = []
        self.relabel()
        for i in sorted(self):
            line = []
            line.append("0")
            line.append(str(i))
            node_id = self.topochecker_relabelling_inverse[i]
            for p in self.predicates[node_id]:
                line.append(p)
            lines += [",".join(line)]
        total = "\n".join(lines)
        # TODO fix this ugliness
        self.relabel(restore=True)
        return total

    def unique_file_id(self):
        return "_" + str(uuid.uuid4())

    def bgkripke_file(self):
        """ create bgkripke_file if it does not exist. This is the same in every invocation."""
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY

        try:
            file_handle = os.open(self.tmppath + 'bgkripke.dot', flags)
        except OSError as e:
            if e.errno == errno.EEXIST:  # Failed as the file already exists
                pass
            else:  # Something unexpected went wrong so reraise the exception
                raise
        else:  # No exception, so the file must have been created successfully
            with os.fdopen(file_handle, 'w') as text_file:
                # Using `os.fdopen` converts the handle to an object
                text_file.write("digraph{\n0;\n}")

    def write_topo_files(self,unique_file_id):
        """ write files before invoking topochecker (which will happen by TopoInvoker). 
        We need this here to keep the SpacePredicatedGraph on states."""

        if not os.path.isfile(self.tmppath + "spacemodel" + ".dot"):
            self.write_spacemodel()

        # with open(self.tmppath + "spacemodel" + unique_file_id + ".dot", "w") as text_file:
            # text_file.write(self.to_dot())
        with open(self.tmppath + "valuations" + unique_file_id + ".csv", "w") as text_file:
            text_file.write(self.topo_csv())
        self.bgkripke_file()


    def write_spacemodel(self):
        with open(self.tmppath + "spacemodel" + ".dot", "w") as text_file:
            text_file.write(self.to_dot())

    def invoke_topochecker(self, spatialprop, topostatements=[]):

        unique_file_id = self.unique_file_id()
        self.write_topo_files(unique_file_id)

        current_invokation_id = "_" + str(uuid.uuid1())
        # self.last_invocation_id = current_invokation_id
        self.last_spatialprop = spatialprop
        # TODO: spatialprop should be a list of props, where we assign some
        # colours


        # invoke_string = """Kripke "bgkripke.dot" Space "spacemodel""" + \
            # unique_file_id + """.dot" Eval "valuations""" + unique_file_id + """.csv";\n"""
        invoke_string = """Kripke "bgkripke.dot" Space "spacemodel.dot" Eval "valuations""" + unique_file_id + """.csv";\n"""

        for statement in topostatements + self.default_topostatements:
            invoke_string += statement + '\n'

        invoke_string += """\nCheck "0xA0DB8E" """ + spatialprop  + ";"

        with open(self.tmppath + "input" + unique_file_id + current_invokation_id + ".topochecker", "w") as text_file:
            text_file.write(invoke_string)

        try:
            out = subprocess.check_output(
                [self.path_to_executable, self.tmppath + "input" + unique_file_id + current_invokation_id + ".topochecker", self.tmppath + "sp" + unique_file_id + current_invokation_id], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            raise TopocheckerException(e)

        colored_lines = [line for line in open(
            self.tmppath + "sp" + unique_file_id + current_invokation_id + "-0.dot") if 'color' in line]
        colour_results = []

        for line in colored_lines:
            # get first number that appears
            state_number = re.search(r'\d+', line).group()
            colour_results.append(
                self.topochecker_relabelling_inverse[int(state_number)])

        if not DEBUG_INVOKER:
            # remove results file
            os.remove(self.tmppath + "sp" + unique_file_id +
                      current_invokation_id + "-0.dot")
            os.remove(self.tmppath + "valuations" + unique_file_id + ".csv")
            # os.remove(self.tmppath + "spacemodel" + unique_file_id + ".dot")
            os.remove(self.tmppath + "input" + unique_file_id +
                      current_invokation_id + ".topochecker")
        return colour_results

    def populate_closurespace_presence_map(self,presence_map):
        """ given a closure space without taxis inside, read a map of {poi_ident:[taxi_id1..]} and put the taxis
            in the respective positions on the closure space   """
        found=False
        for poi_ident, taxis in presence_map.items():    
            # print poi_ident,taxis
            for taxi_ident in taxis:
                for node in self.nodes():
                    for predicate in self.predicates[node]:
                        if predicate == 'Tid'+str(taxi_ident):
                            # delete it from list self.node[node]
                            # self.predicates[].append(newp)
                            self.predicates[node].remove('Tid'+str(taxi_ident))
                            # delete also one 'taxi' predicate
                            self.predicates[node].remove('taxi')
                            # print 'Tid'+str(taxi_ident)
                            found=True
                            break
                    if found==True:
                        found=False
                        break
        for poi_ident, taxis in presence_map.items():    
            for taxi_ident in taxis:
                self.predicates[poi_ident].append('taxi')
                self.predicates[poi_ident].append('Tid'+str(taxi_ident))  
        return self
