import boto3
import sys
from datetime import datetime, timedelta
client = boto3.client('cloudwatch')
response = client.get_metric_statistics(
    Namespace='AWS/EC2',
    MetricName='CPUUtilization',
    Dimensions=[
        {
        'Name': 'InstanceId',
        'Value': 'i-0ddd81da0a5595c72'
        },
    ],
    StartTime=datetime.utcnow() - timedelta(days=2),
    #StartTime=datetime(2018, 8, 6) - timedelta(days=2),
    EndTime=datetime.utcnow(),
    #EndTime=datetime(2018, 8, 7),
    Period=86400,
    Statistics=[
        'Average',
    ],
    Unit='Percent'
)

#print response
for cpu in response['Datapoints']:
	if 'Average' in cpu:
		print(cpu['Average'])
	

