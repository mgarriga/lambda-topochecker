# Spacial properties checking as microservices for IoT deployments

# Experiment ONE: 1000 events, change time multipliers to increase paralelism

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

## lambda
cost (approx): number of calls * avg seconds per call * $ per 1000 miliseconds with 1536 memory in lambda
(max memory used in the range of 300 -- 400 so the config could be adjusted... but this would affect the number of vCPUs)

### Experiment v1

max 32.797850132

min 8.67687916756

avg 20.6947725175

### Experiment v2

Process total times:

max 30.3305289745

min 6.78941106796

avg 19.7226203169

Process checking times:

max 28.9426138401

min 1

avg 14.7753132978

Process wait times:

max 29.3305289745

min 0.698618173599

avg 4.94730701909

---

Process total times:

max 30.2911410332

min 7.02629303932

avg 20.4447795384

Process checking times:

max 28.8596880436

min 1

avg 14.7760718247

Process wait times:

max 29.2911410332

min 0.697234869003

avg 5.66870771371

### Experiment v3
Counting errors, time multiplier * 5 to avoid  5xx responses from api gateway / Load balancer
* Run 1
Process total times:
max 54.3187029362
min 10.1929910183
avg 20.554023526
Process checking times:
max 28.799352169
min 1
avg 16.8449816718
Process wait times:
max 31.0119028091
min 0.712862730026
avg 3.70904185418
Number of errors:  59

---
Process total times:
max 30.2534110546
min 6.62986207008
avg 18.5572035753
Process checking times:
max 28.8283851147
min 1
avg 15.2255490777
Process wait times:
max 29.2534110546
min 0.695712089539
avg 3.33165449756
Number of errors:  43

* time_mult 5
Process total times:
max 34.9515209198
min 7.75299215317
avg 18.953984548
median 17.308190465

Process checking times:
max 28.8671591282
min 1
avg 14.7619543142

Process wait times:
max 33.9515209198
min 0.702660799026
avg 4.19203023383

Number of errors:  67

* time_mult 10

Process total times:
max 30.2915019989
min 6.533618927
avg 20.2013915217
median 19.6651741266

Process checking times:
max 28.9538729191
min 1
avg 15.1260486855

Process wait times:
max 29.2915019989
min 0.687526226044
avg 5.07534283622

Number of errors:  89

* time_mult 15
Process total times:
max 30.3206238747
min 10.2256159782
avg 21.8692738872
median 22.1156170368

Process checking times:
max 28.9224588871
min 1
avg 15.3014224413
median 22.1156170368

Process wait times:
max 29.3206238747
min 0.70365691185
avg 6.56785144587
Number of errors:  124

* time mult 20

Process total times:
median 25.8362128735

Process checking times:
max 28.8981289864
min 1
avg 14.604147533
median 25.8362128735

Process wait times:
max 29.3464591503
min 0.717052936554
avg 9.48029865551

Number of errors:  235

* time mult 30

Process total times:
max 30.3122909069
min 10.3466999531
avg 24.960494148
median 28.8509440422

Process checking times:
max 28.9702630043
min 1
avg 11.5299053924

Process wait times:
max 29.3122909069
min 0.743782997131
avg 13.4305887556

Number of errors:  335

* time mult 40

Process total times:
max 30.4740028381
min 6.80550003052
avg 23.9449834871
median 27.4247710705

Process checking times:
max 28.9559519291
min 1
avg 10.2797317222

Process wait times:
max 29.4740028381
min 0.687190055847
avg 13.6652517649

Number of errors:  302


## traditional cloud

cost (rough approach): 8hs/day * 15 instances + 8 hs/day * 10 instances + 8 hs/day * 5 instances

max 66.4608018398

min 2.03265595436

avg 58.001706005

__Obs__: maybe we should not multiply the time that much to give the opportunity to scale up/down, since when the experiment ended, the Autoscaling group was on 8/9 instances and still trying to spin more (i.e., the capacity was still low).

### Time Mult: 10

max 65.8290259838
min 10.5190088749
avg 52.2841121855
median 61.0214465857

Process checking times:
max 28.7686941624
min 1
avg 4.77198692948

Process wait times:
max 64.8290259838
min 0.83674120903
avg 47.512125256
Number of errors:  475


Process total times:
max 62.203122139
min 6.98474812508
avg 54.8065455694
median 61.034273982

Process checking times:
max 26.5238289833
min 1
avg 3.3148269443

Process wait times:
max 61.203122139
min 0.821813821793
avg 51.4917186251
Number of errors:  533


Process total times:
max 66.0883948803
min 1.01836490631
avg 57.8627860903
median 61.0314071178

Process checking times:
max 26.3251690865
min 1
avg 2.07949230767

Process wait times:
max 65.0883948803
min 0.018364906311
avg 55.7832937826
Number of errors:  642

Process total times:
max 61.1026849747
min 7.60310602188
avg 57.5767112926
median 61.0349448919

Process checking times:
max 16.059789896
min 1
avg 2.381725652

Process wait times:
max 60.1026849747
min 0.831492900848
avg 55.1949856406
Number of errors:  632

## super big instance:
64 cores!
Cost: 2300 eur per month with the instance 100% uptime

__Obs__: With TIME_MULTIPLIER=20 all cores were at 100%. With  TIME_MULTIPLIER=10, the results were the following (it still outperforms lambda with this config):

max 17.0334839821

min 13.9760069847

avg 15.2778843108

---
### Exp v3 --- time mult 5
Process total times:
max 17.1205840111
min 7.00501418114
avg 9.50717100167
Process checking times:
max 16.4422981739
min 6.52919983864
avg 8.84256912567
Process wait times:
max 0.740673065186
min 0.47151517868
avg 0.664601876008
Number of errors:  0


### Exp v3 --- time mult 10
Process total times:
max 18.5418870449
min 7.15218687057
avg 9.89759757878
Process checking times:
max 17.8530209064
min 6.64702796936
avg 9.23224905039
Process wait times:
max 0.744853019714
min 0.47875213623
avg 0.665348528397
Number of errors:  0

### 15
Process total times:
max 20.7205638885
min 4.86521697044
avg 10.1811501642
Process checking times:
max 20.038424015
min 4.38161277771
avg 9.51728112706
Process wait times:
max 0.744230270386
min 0.467406988144
avg 0.663869037112
Number of errors:  0


### 20

max 32.027230978
min 4.92436718941
avg 12.2027784039
Process checking times:
max 31.3118159771
min 4.41846489906
avg 11.5379735266
Process wait times:
max 0.906223773956
min 0.472197771072
avg 0.664804877349
Number of errors:  0

### 30

Process total times:
max 41.6801199913
min 5.00288295746
avg 19.5489675577
Process checking times:
max 26.5577149391
min 4.52281713486
avg 15.5194784415
Process wait times:
max 17.8412408829
min 0.463512897491
avg 4.02948911626
Number of errors:  0

### 40
Process total times:
max 63.5076060295
min 5.13222908974
avg 28.786947272
Process checking times:
max 31.7129402161
min 4.65086197853
avg 17.076183942
Process wait times:
max 41.0344619751
min 0.467218160629
avg 11.71076333
Number of errors:  0


### 50

Process total times:
max 73.3106851578
min 5.26674199104
avg 34.4345297466
Process checking times:
max 27.7353339195
min 4.7897799015
avg 17.5984658824
Process wait times:
max 53.065969944
min 0.472991228104
avg 16.8360638642
Number of errors:  0

### 60
Process total times:
max 99.5162239075
min 5.0516409874
avg 40.6685361296
Process checking times:
max 27.0700190067
min 4.57554316521
avg 18.0946975606
Process wait times:
max 78.2983567715
min 0.465889930725
avg 22.573838569
Number of errors:  0
