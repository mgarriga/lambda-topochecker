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

* tm 15
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

* tm 20

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

* tm 30

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


# NEW EXPERIMENT Hybrid
Lambda + ec2 + exp in mypc
Time mult = 3
Process total times:
max 17.6253290176
min 5.11400389671
avg 10.1647513151
median 8.74271500111
Process checking times:
max 5.55545401573
min 2.52032613754
avg 3.45181058884
median 3.17547392845
Process wait times:
max 14.5118529797
min 2.2135488987
avg 6.71294072628
median 5.31389260292
Number of errors:  0

ec2 only + exp in mypc
Process total times:
max 19.2044949532
min 5.26402688026
avg 11.0652651167
median 10.9982479811
Process checking times:
max 3.43657398224
min 2.57009315491
avg 3.13670302868
median 3.15740704536
Process wait times:
max 15.8406391144
min 2.54561185837
avg 7.92856208801
median 7.74494040012
Number of errors:  0

Lambda + ec2 + exp in ec2
Process total times:
max 15.7430620193
min 2.86375713348
avg 7.76667461872
median 6.514134883880615
Process checking times:
max 5.39462804794
min 2.62148094177
avg 3.40432742596
median 3.159324884414673
Process wait times:
max 12.6369099617
min 0.122668027878
avg 4.36234719276
median 2.9811580181121826
Number of errors:  0

ec2 + exp in ec2 only
Process total times:
max 17.2425279617
min 2.78031182289
avg 9.04925213814
median 8.921335458755493
Process checking times:
max 3.48141098022
min 2.57014203072
avg 3.13005836964
median 3.169420003890991
Process wait times:
max 13.879858017
min 0.117774009705
avg 5.9191937685
median 5.636520504951477
Number of errors:  0


# NEW EXPERIMENT Hybrid
Lambda + ec2 + exp in mypc
Time mult = 5

ec2 + exp in ec2 only
Process total times:
max 19.584813118
min 6.99519491196
avg 10.4024457598
median 10.4606910944

Process checking times:
max 19.4878270626
min 6.74331498146
avg 10.2884221238
median 10.3191665411

Process wait times:
max 0.68451499939
min 0.0723438262939
avg 0.114023635983
median 0.103654026985
Number of errors:  0

lambda calls:  0
vm calls:  400

Timemult = 10
Process total times:
max 17.8742311001
min 4.89766407013
avg 10.1326728237
median 10.4515545368

Process checking times:
max 17.7753441334
min 4.77481412888
avg 10.0281756151
median 10.358093977

Process wait times:
max 0.770931959152
min 0.0711030960083
avg 0.104497208595
median 0.0944249629974
Number of errors:  0

lambda calls:  0
vm calls:  400

Time mult = 15
Process total times:
max 16.2250239849
min 2.35653996468
avg 11.2271127247
median 11.6476889849

Process checking times:
max 16.1324779987
min 2.27614808083
avg 11.1110134076
median 11.5473530293

Process wait times:
max 1.74105405807
min 0.0717988014221
avg 0.116099317127
median 0.0968449115753
Number of errors:  0

lambda calls:  0
vm calls:  536

Timemult = 20
Process total times:
max 24.3378558159
min 5.26496815681
avg 11.3983225397
median 11.6297380924

Process checking times:
max 22.9995968342
min 5.12817716599
avg 11.2849685671
median 11.4529914856

Process wait times:
max 1.78074407578
min 0.0723948478699
avg 0.113353972634
median 0.0972969532013
Number of errors:  0

lambda calls:  0
vm calls:  432

Timemult = 30
Process total times:
max 50.1348090172
min 9.46761107445
avg 27.4386394957
median 29.149902463

Process checking times:
max 50.011111021
min 1
avg 16.3184409754
median 16.2234475613

Process wait times:
max 30.0018889904
min 0.0744049549103
avg 11.1201985202
median 4.11209499836
Number of errors:  388

lambda calls:  492
vm calls:  648

Timemult = 40
Process total times:
max 49.315664053
min 6.65264606476
avg 22.9555531137
median 23.27439785

Process checking times:
max 35.8799600601
min 1
avg 17.8487885557
median 17.6827769279

Process wait times:
max 28.5121760368
min 0.0744140148163
avg 5.10676455796
median 0.131311178207
Number of errors:  75

lambda calls:  90
vm calls:  469

timemult = 50
Process total times:
max 47.1267080307
min 7.50482177734
avg 28.2301386703
median 29.1480255127

Process checking times:
max 35.7286949158
min 1
avg 15.6928616809
median 16.3879308701

Process wait times:
max 30.1682069302
min 0.0763399600983
avg 12.5372769893
median 10.6121250391
Number of errors:  359

lambda calls:  465
vm calls:  595

timemult = 50
Process total times:
max 52.578248024
min 7.83571004868
avg 28.5438329359
median 29.1514868736

Process checking times:
max 35.2668721676
min 1
avg 15.7148884318
median 16.5022280216

Process wait times:
max 31.9544150829
min 0.0735449790955
avg 12.8289445041
median 9.41698336601
Number of errors:  377

lambda calls:  500
vm calls:  595
