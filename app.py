import boto3
import sys
from datetime import datetime, timedelta


# app.py

from flask import Flask
from flask import request
app = Flask(__name__)

# here is how we are handling routing with flask:
last = 999
lastdatetime = datetime.utcnow()

@app.route('/')
class HealthCheck():
    def get():
        return {'status':'up'}

@app.route('/check/<string:spatialprop>')
def get(spatialprop):
    global last
    global lastdatetime
    print(str(spatialprop))
    if last != 999:
        if lastdatetime + timedelta(seconds=30) >= datetime.utcnow(): 
            print("cache")
            print(str(last))
            if last <80:
                return(str(last) + " Call VM")
            else:
                return(str(last) + "Call Lambda")    
    iid = request.args.get('iid')
    print(iid)
    if iid == None:
        iid = 'i-0ddd81da0a5595c72'
    client = boto3.client('cloudwatch')
    response = client.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[
            {
            'Name': 'InstanceId',
            'Value': iid
            },
        ],
        StartTime=datetime.utcnow() - timedelta(seconds=120),
        #StartTime=datetime(2018, 8, 6) - timedelta(days=2),
        EndTime=datetime.utcnow(),
        #EndTime=datetime(2018, 8, 7),
        Period=60,
        Statistics=[
            'Average',
        ],
            Unit='Percent'
    )

    #print response
    for cpu in response['Datapoints']:
        if 'Average' in cpu:
            print(cpu['Average'])
            last = cpu['Average']
            print(str(last) + " Last CPU")
        
    lastdatetime=datetime.utcnow()
    if last <80:
        return(str(last) + " Call VM")
    else:
        return(str(last) + " Call Lambda")    
    
        # TODO implement
# include this for local dev

if __name__ == '__main__':
    app.run()
