## Experiment ONE: 1000 events, TIME_MULTIPLIER 10

IMPORTANT: change tornado setup:
* server.start(#CPUs):
* for lambda should be one -- OK
* for traditional cloud should be one -- OK
* for the big instance should be 72 -- OK
* (for local, according to the #cores)
* Start with 5 instances and scale up to 15 -- OK

 ### Experimental setup
```
NUM_PROCESSES = 100
 TIMEOUT = 30
 TIME_MULTIPLIER = 10 # should be an int
 MAX_LIMIT_TAXIPRESENCES = 1000
 BEIJING_TIMELEN = 3600 * 1  # one hour
 BEIJING_STARTDATETIME = "2008-02-05 11:00:16"
```

### lambda
max 32.797850132

min 8.67687916756

avg 20.6947725175

### traditional cloud
max 66.4608018398

min 2.03265595436

avg 58.001706005

__Obs__: maybe we should not multiply the time that much to give the opportunity to scale up/down, since when the experiment ended, the Autoscaling group was on 8/9 instances and still trying to spin more (i.e., the capacity was still low).

### super big instance:
72 cores!

__Obs__: With TIME_MULTIPLIER=20 all cores were at 100%. With  TIME_MULTIPLIER=10, the results were the following (it still outperforms lambda with this config):

max 17.0334839821

min 13.9760069847

avg 15.2778843108
