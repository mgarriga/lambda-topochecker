# Spacial properties checking as microservices for IoT deployments

# Experiment ONE: 1000 taxipresences max, change time multipliers to increase paralelism

TaxiPresences in window 536 MAX_LIMIT_TAXIPRESENCES 1000

### Experimental setup
```
NUM_PROCESSES = 100
 TIMEOUT = 30
 TIME_MULTIPLIER = 5 # 10 20 40 should be an int
 MAX_LIMIT_TAXIPRESENCES = 1000
 BEIJING_TIMELEN = 3600 * 1  # one hour
 BEIJING_STARTDATETIME = "2008-02-05 11:00:16"
```

## lambda
* cost (approx): number of calls * avg seconds per call * $ per 1000 miliseconds with 1536 memory in lambda
(max memory used in the range of 300 -- 400 so the config could be adjusted... but this would affect the number of vCPUs)

* Integration timeout 	50 milliseconds - 29 seconds for all integration types, including Lambda, Lambda proxy, HTTP, HTTP proxy, and AWS integrations. 	Not configurable as for the lower or upper bounds.

### Experiment V4

`TIME_MULTIPLIER = 5`
Process total times:
max 24.5938961506
min 6.22892403603
avg 12.0729448285
median 11.8305020332
Process checking times:
max 22.8470549583
min 5.45260000229
avg 11.1075751871
median 10.9244329929
Process wait times:
max 5.23234629631
min 0.679046154022
avg 0.965369641427
median 0.910706996918
Number of errors:  0


`TIME_MULTIPLIER = 10`

Process total times:
max 25.9491829872
min 5.5252161026
avg 12.2336736887
median 12.0114378929
Process checking times:
max 23.0006577969
min 4.79077410698
avg 11.2179365703
median 10.9412379265
Process wait times:
max 7.74454712868
min 0.669422864914
avg 1.01573711835
median 0.908437013626
Number of errors:  0

`TIME_MULTIPLIER = 20`

Process total times:
max 25.0398960114
min 5.63814806938
avg 11.9353128772
median 11.7818849087
Process checking times:
max 23.261713028
min 4.90805506706
avg 11.0026817331
median 10.8799638748
Process wait times:
max 5.87660884857
min 0.649884939194
avg 0.932631144085
median 0.883970022202
Number of errors:  0

`TIME_MULTIPLIER = 40`

Process total times:
max 25.5190460682
min 6.90674805641
avg 13.1635449244
median 12.8291418552
Process checking times:
max 23.4939148426
min 6.11652493477
avg 12.0691477903
median 11.7453069687
Process wait times:
max 2.79546809196
min 0.661566019058
avg 1.09439713412
median 0.905403137207
Number of errors:  0


`TIME_MULTIPLIER = 60`

Process total times:
max 25.0595691204
min 9.60536694527
avg 14.2084693539
median 13.9722318649
Process checking times:
max 23.1489100456
min 8.49098277092
avg 12.9109556822
median 12.8426949978
Process wait times:
max 3.27529191971
min 0.714883089066
avg 1.29751367171
median 1.24377202988
Number of errors:  0


## traditional cloud

* cost (rough approach): 8hs/day * 15 instances + 8 hs/day * 10 instances + 8 hs/day * 5 instances

__Obs__: maybe we should not multiply the time that much to give the opportunity to scale up/down, since when the experiment ended, the Autoscaling group was on 8/9 instances and still trying to spin more (i.e., the capacity was still low).

### Experiment V4

`TIME_MULTIPLIER = 5`

Process total times:
max 126.037056923
min 14.2434010506
avg 105.38300167
median 120.964949131
Process checking times:
max 23.057926178
min 1
avg 4.18019169077
median 1.0
Process wait times:
max 125.037056923
min 0.798776865005
avg 101.202809979
median 119.964949131
Number of errors:  226

`TIME_MULTIPLIER = 10`

Process total times:
max 125.979536057
min 7.06077289581
avg 93.5846644177
median 120.950695395
Process checking times:
max 16.5619399548
min 1r
avg 5.61123898892
median 1.0
Process wait times:
max 124.979536057
min 0.761703014374
avg 87.9734254288
median 119.950695395
Number of errors:  327

`TIME_MULTIPLIER = 20`

Process total times:
max 121.087191105
min 15.8196640015
avg 111.342014894
median 120.969104409
Process checking times:
max 28.8592369556
min 1
avg 2.32829847864
median 1.0
Process wait times:
max 120.087191105
min 0.660028934479
avg 109.013716415
median 119.969104409
Number of errors:  466

`TIME_MULTIPLIER = 40`

## super big instance:
64 cores, on AZURE
* Cost: 2300 eur per month with the instance 100% uptime

__Obs__: With TIME_MULTIPLIER=20 all cores were at 100%. With  TIME_MULTIPLIER=10, the results were the following (it still outperforms lambda with this config):

### Experiment V4

`TIME_MULTIPLIER = 5`

Process total times:
max 12.165514946
min 4.88823080063
avg 9.27915285042
median 9.44873595238
Process checking times:
max 11.5176839828
min 4.42849493027
avg 8.64692096567
median 8.76832008362
Process wait times:
max 2.27733802795
min 0.451345920563
avg 0.632231884757
median 0.649231910706
Number of errors:  0


`TIME_MULTIPLIER = 10`

Process total times:
max 12.3012151718
min 4.88013315201
avg 9.50754943774
median 9.7054554224
Process checking times:
max 11.6551630497
min 4.4278819561
avg 8.88011479945
median 9.04520404339
Process wait times:
max 0.70650601387
min 0.446630001068
avg 0.627434638285
median 0.652963161469
Number of errors:  0


`TIME_MULTIPLIER = 20`

Process total times:
max 42.5363180637
min 8.19946980476
avg 15.5619276526
median 12.8700449467
Process checking times:
max 41.8551259041
min 7.71455001831
avg 14.8170027466
median 12.2840945721
Process wait times:
max 3.00169968605
min 0.442948102951
avg 0.74492490603
median 0.651254057884
Number of errors:  0

`TIME_MULTIPLIER = 40`

Process total times:
max 72.6872639656
min 5.00675415993
avg 32.4289947491
median 27.360325098
Process checking times:
max 29.8207709789
min 4.53101301193
avg 18.2806551494
median 19.9813210964
Process wait times:
max 48.9951038361
min 0.446217060089
avg 14.1483395997
median 6.22955727577
Number of errors:  0


`TIME_MULTIPLIER = 60`
Process total times:
max 104.753088951
min 5.49005484581
avg 44.0520987648
median 39.7514150143
Process checking times:
max 30.9633231163
min 5.02510285378
avg 19.2033069002
median 20.608590126
Process wait times:
max 78.0513429642
min 0.448193073273
avg 24.8487918646
median 17.2226130962
Number of errors:  0
