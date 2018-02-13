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
import argparse

from numpy import median

# db.createUser({user: 'china',pwd: 'chairmanmaoiswatching', roles: [{ role: 'readWrite', db:'chinadb'}]})
# mongo -u china -p chairmanmaoiswatching  128.199.57.234:27017/chinadb

# db = connect(
# 	db='chinadb',
# 	host='mongodb://china:chairmanmaoiswatching@128.199.57.234/chinadb'
# )



# db = connect('chinadb')

errcount = 0

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
        global errcount
        start_time = time.time()
        resp = requests.post(config['state_keeper_serverport'] +
                             '/update', json=self.jsontask)
        resp = requests.get(config['checker_serverport'] +
        '/check/R%28%5Btaxi%5D%2C%28%5BTRANSPORTSUBWAY%5D%20%7C%20%5BTRANSPORTBUSSTOP%5D%29%2C%5BFOODBAR%5D%29%20%26%20%28N%20%5BTRANSPORTFUEL%5D%29%20')
        #                    '/check/%28N%20%5BTRANSPORTBUSSTOP%5D%29')
        if resp.status_code >= 500:
            print 'RequestTask got ' + str(resp.status_code)
            # return -1
            resp_json = json.loads('{"mc_time":1}')
        #print resp
        # TODO here the load balancer and api gateway are returning 504, maybe they can be handled similarly
        #if not u'mc_time' in resp.json():
        #    print 'PROBLEMA:'
        #    print resp.json()
        #    resp = json.loads('{"mc_time":1}')
            errcount = errcount + 1
        else:
            resp_json = resp.json()
        print resp_json
        end_time = time.time()
        wait_time = (end_time - start_time) - resp_json[u'mc_time']
        print 'requesttask: took', "{0:.2f}".format(end_time - start_time), "sec", '- waited',"{0:.2f}".format(wait_time)
        return { "wait_time":wait_time, "mc_time":resp_json[u'mc_time'], "total_time":{self.presence_datetime: end_time - start_time}, "errcount":errcount}

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

    # NUM_PROCESSES = 100
    # TIMEOUT = 30
    # TIME_MULTIPLIER = 5 # should be an int
    # MAX_LIMIT_TAXIPRESENCES = 10
    # BEIJING_TIMELEN = 3600 * 1  # one hour
    # BEIJING_STARTDATETIME = "2008-02-05 11:00:16"
    # Experimental setup OK
    NUM_PROCESSES = 300
    TIMEOUT = 30
    TIME_MULTIPLIER = 20 # should be an int
    MAX_LIMIT_TAXIPRESENCES = 1000
    BEIJING_TIMELEN = 3600 * 1  # one hour
    BEIJING_STARTDATETIME = "2008-02-05 11:00:16"


    parser = argparse.ArgumentParser()
    parser.add_argument("config_file")
    args = parser.parse_args()
    print args.config_file
    # config = json.load(open('config_setup.json'))
    config = json.load(open(args.config_file))

    print 'Loaded current config', config

    db = connect(
        db=config['db'],
        host=config['dbhost']
    )

    print 'Resetting state keeeper.'
    requests.get(config['state_keeper_serverport']+"/empty")


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

    total_times = [i['total_time'] for i in lr]
    mc_times = [i['mc_time'] for i in lr]
    wait_times = [i['wait_time'] for i in lr]
    errors = [i['errcount'] for i in lr]

    print 'Process total times:'
    onlytimes = [[v for k, v in listitem.iteritems()][0] for listitem in total_times]
    print 'max', max(onlytimes)
    print 'min', min(onlytimes)
    print 'avg', float(sum(onlytimes)) / max(len(onlytimes), 1)
    print 'median', median(onlytimes)

    print 'Process checking times:'
    print 'max', max(mc_times)
    print 'min', min(mc_times)
    print 'avg', float(sum(mc_times)) / max(len(mc_times), 1)
    print 'median', median(mc_times)

    print 'Process wait times:'
    print 'max', max(wait_times)
    print 'min', min(wait_times)
    print 'avg', float(sum(wait_times)) / max(len(wait_times), 1)
    print 'median', median(wait_times)
    print 'Number of errors: ', sum(errors)
