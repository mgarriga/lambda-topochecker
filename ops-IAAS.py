# -*- coding: utf-8 -*-
from mongoengine import *
import csv
from datetime import datetime, timedelta
from pprint import pprint
import glob
import time
import networkx as nx
import time
import os
import requests
from mongoengine.queryset.visitor import Q
try:
    import cPickle as pickle
except:
    import pickle

# db = connect('chinadb')
# db.createUser({user: 'china',pwd: 'chairmanmaoiswatching', roles: [{ role: 'readWrite', db:'chinadb'}]})
# mongo -u china -p chairmanmaoiswatching  128.199.57.234:27017/chinadb

db = connect(
    db='chinadb',
    host='mongodb://china:chairmanmaoiswatching@128.199.57.234/chinadb'
)


class POI(Document):
                # https://github.com/MorbZ/OsmPoisPbf
    name = StringField()
    ident = StringField()  # OSM-ID
    poi_type = StringField()
    point = PointField(auto_index=True)
    presences_here = IntField(default=0)


class TaxiPresence(Document):
    taxi_ident = StringField()  # OSM-ID
    presence_datetime = DateTimeField(index=True)
    poi_point = ReferenceField('POI')
    initial = BooleanField(default=False)
    next = ReferenceField('self')
    meta = {
        'indexes': [
            'presence_datetime',
        ]
    }


if __name__ == '__main__':
    print 'Simulating TaxiPresence stream from', TaxiPresence.objects.order_by('presence_datetime')[0].presence_datetime
    prev = None
    for taxipresence in TaxiPresence.objects.order_by('presence_datetime'):
        if prev:
            # now sleep until the next TaxiPresence timestamp
            wait_time = taxipresence.presence_datetime - prev.presence_datetime
            # to next den einai next temporally, einai to next gia to idio taxi!!
            # akyro
            print 'fake sleeping for', wait_time.total_seconds()
            # time.sleep(wait_time.total_seconds())
            time.sleep(10)
        # update
        task = {taxipresence.poi_point.ident: taxipresence.taxi_ident}
        print task
        # LOCAL
        #resp = requests.post('http://127.0.0.1:5001/update', json=task)
        #resp = requests.post('http://10.79.11.36:5001/update', json=task)
        # EC2
        resp = requests.post('http://35.167.250.213:5001/update', json=task)

        # check
        # LOCAL
        print "checking"
        #resp = requests.get('http://10.79.11.36:5000/check/(N%20[TRANSPORTBUSSTOP])')
        #resp = requests.get('http://127.0.0.1:5000/check/(N%20[TRANSPORTBUSSTOP])')

        #EC2 (single instance)
        #resp = requests.get('http://52.42.97.232:5000/check/(N%20[TRANSPORTBUSSTOP])')

        #Load Balancer
        resp = requests.get('http://topochecker-load-balancer-375081757.us-west-2.elb.amazonaws.com:5000/check/(N%20[TRANSPORTBUSSTOP])')

        #resp = requests.get('https://qiz6l70gm4.execute-api.us-west-2.amazonaws.com/dev/check/')
        print resp
        prev = taxipresence
