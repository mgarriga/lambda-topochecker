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
import dateutil
import sys
try:
    import cPickle as pickle
except:
    import pickle
import multiprocessing
import Queue
import json


config = json.load(open('config_setup.json'))

print 'Loaded current config', config
# db.createUser({user: 'china',pwd: 'chairmanmaoiswatching', roles: [{ role: 'readWrite', db:'chinadb'}]})
# mongo -u china -p chairmanmaoiswatching  128.199.57.234:27017/chinadb

# db = connect(
# 	db='chinadb',
# 	host='mongodb://china:chairmanmaoiswatching@128.199.57.234/chinadb'
# )

db = connect(
    db=config['db'],
    host=config['dbhost']
)

# db = connect('chinadb')


class POI(Document):
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


class Requestor(multiprocessing.Process):

    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                # Poison pill means shutdown
                self.task_queue.task_done()
                break
            answer = next_task()
            self.task_queue.task_done()
            self.result_queue.put(answer, block=True)
        return


class RequestTask(object):
    """ send checking request, count time it took to get result, put result in the result_queue """

    def __init__(self, jsontask):
        self.jsontask = jsontask

        self.presence_datetime = jsontask['presence_init_time']
        del self.jsontask['presence_init_time']

    def __call__(self):
        start_time = time.time()
        resp = requests.post(config['state_keeper_serverport'] +
                             '/update', json=self.jsontask)
        resp = requests.get(config['checker_serverport'] +
                            '/check/%28N%20%5BTRANSPORTBUSSTOP%5D%29')
        if resp.status_code == 500:
            print 'RequestTask got 500.'
            return -1
        end_time = time.time()
        print 'requesttask: took', "{0:.2f}".format(end_time - start_time), "sec"
        return {self.presence_datetime: end_time - start_time}


def addSecs(fulldate, secs):
    fulldate = fulldate + timedelta(seconds=secs)
    return fulldate


def subtractSecs(fulldate, secs):
    fulldate = fulldate - timedelta(seconds=secs)
    return fulldate

if __name__ == '__main__':
    """ NUM_PROCESSES will start making requests based on a limit of MAX_LIMIT_TAXIPRESENCES
    starting from BEIJING_STARTDATETIME for seconds specified in BEIJING_TIMELEN. Time may be adjusted by TIME_MULTIPLIER.
     Tuesday "2008-02-05 11:00:16" is the lunchtime request peak. """

    NUM_PROCESSES = 100
    TIMEOUT = 30
    TIME_MULTIPLIER = 2 # should be an int
    MAX_LIMIT_TAXIPRESENCES = 10
    BEIJING_TIMELEN = 3600 * 1  # one hour
    BEIJING_STARTDATETIME = "2008-02-05 11:00:16"

    # start of dataset, for debugging
    # start_timeslot = TaxiPresence.objects.order_by('presence_datetime')[0].presence_datetime
    start_timeslot = TaxiPresence.objects((Q(presence_datetime__gte=dateutil.parser.parse(
        BEIJING_STARTDATETIME)))).order_by('presence_datetime')[0].presence_datetime
    in_window = TaxiPresence.objects((Q(presence_datetime__lte=addSecs(start_timeslot, BEIJING_TIMELEN)) & Q(
        presence_datetime__gt=start_timeslot)))[:MAX_LIMIT_TAXIPRESENCES]

    # get initial positions BEIJING_TIMELEN before start_timeslot to populate
    # initially the clspace
    initial_positions = TaxiPresence.objects((Q(presence_datetime__lte=start_timeslot) & Q(
        presence_datetime__gt=subtractSecs(start_timeslot, BEIJING_TIMELEN))))[:MAX_LIMIT_TAXIPRESENCES]
    init_left = initial_positions.count()
    print 'Setting initial positions from taxipresences since', subtractSecs(start_timeslot, BEIJING_TIMELEN), 'progress left:'
    for taxipresence in initial_positions:
        init_left -= 1
        resp = requests.post(config['state_keeper_serverport'] + '/update',
                             json={taxipresence.poi_point.ident: taxipresence.taxi_ident})
        if init_left % 33 == 0:
            print init_left, '..',
            sys.stdout.flush()
    print 'done.'

    print 'Simulating TaxiPresence stream from', start_timeslot
    print 'TaxiPresences in window', in_window.count(), 'MAX_LIMIT_TAXIPRESENCES', MAX_LIMIT_TAXIPRESENCES
    left = in_window.count()
    prev = None
    unchecked_tasks = multiprocessing.JoinableQueue(maxsize=300)
    results = multiprocessing.Queue()

    print 'Spawning %d requestors.' % NUM_PROCESSES
    requestors = [Requestor(unchecked_tasks, results)
                  for i in xrange(NUM_PROCESSES)]
    for w in requestors:
        w.start()

    batch = in_window
    for taxipresence in batch.order_by('presence_datetime'):
        if prev:
            # now sleep until the next TaxiPresence timestamp
            wait_time = (taxipresence.presence_datetime -
                         prev.presence_datetime) / TIME_MULTIPLIER
            left -= 1
            print 'main: sleeping for', wait_time.total_seconds(), 'left', left, 'beijing time', taxipresence.presence_datetime
            time.sleep(wait_time.total_seconds())
        task = {taxipresence.poi_point.ident: taxipresence.taxi_ident,
                'presence_init_time': taxipresence.presence_datetime}
        unchecked_tasks.put(RequestTask(jsontask=task))
        prev = taxipresence

    # taxipresences finished, requestors should die now
    for i in xrange(NUM_PROCESSES):
        unchecked_tasks.put(None)
    print 'main: added requestor poison pills.'

    time.sleep(5)
    while not unchecked_tasks.empty():
        time.sleep(1)

    lr = []
    while not results.empty():
        lr.append(results.get(block=True, timeout=TIMEOUT))
    print 'requests len', len(lr)

    # lr is [{presence_init_time: request total time}]
    onlytimes = [[v for k, v in listitem.iteritems()][0] for listitem in lr]

    print 'max', max(onlytimes)
    print 'min', min(onlytimes)
    print 'avg', float(sum(onlytimes)) / max(len(onlytimes), 1)