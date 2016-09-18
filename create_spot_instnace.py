import sys
import boto3
import boto3.ec2
from datetime import datetime, timedelta
import json

aws_access_key_id = sys.argv[1]
aws_secret_access_key = sys.argv[2]
region_name = 'us-east-1'
account_number = '754922593538'
request_duration = 120

s = boto3.Session(aws_access_key_id=aws_access_key_id,
                  aws_secret_access_key=aws_secret_access_key,
                  region_name=region_name)

ec2 = s.client('ec2')

end_time = datetime.now()
start_time = end_time - timedelta(hours=1)
instance_type = ['m3.large']
product_descriptions = ['Linux/UNIX']
availability_zones =  ['us-east-1b' , 'us-east-1c', 'us-east-1d', 'us-east-1e']
subnet_az_mapping = {'us-east-1b': 'subnet-da5b4af2', 'us-east-1c':'subnet-9c9641eb', 'us-east-1d':'subnet-1c679145', 'us-east-1e' : 'subnet-5dacce67'}
expected_bid_price_mapping = { 'm4.large' : '0.088', 'm3.large' : '0.093'}
bid_price_mapping = {}

## request price history and get the latest price per AZ
for az in availability_zones:
    sfip = ec2.describe_spot_price_history(
        StartTime=start_time,
        EndTime=end_time,
        InstanceTypes=instance_type,
        ProductDescriptions=product_descriptions,
        AvailabilityZone=az
    )
    bid_price_mapping[az] = float(sfip['SpotPriceHistory'][0]['SpotPrice'])

# print bid_price_mapping
print bid_price_mapping
bid_price,bid_az = min((v,k) for k,v in bid_price_mapping.items())
bid_subnet = [v for k, v in subnet_az_mapping.iteritems() if k == bid_az]
print bid_price, ' ', bid_az, ' ', bid_subnet[0]

## request spot fleet instance
# sfir = ec2.request_spot_fleet(
#     SpotFleetRequestConfig={
#         'SpotPrice': expected_bid_price_mapping[instance_type[0]],
#         'TargetCapacity': 1,
#         'ValidFrom': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
#         'ValidUntil': (end_time + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%SZ'),
#         'TerminateInstancesWithExpiration': True,
#         'IamFleetRole': 'arn:aws:iam::754922593538:role/iamfleetrole',
#         'LaunchSpecifications': [
#             {
#                 'ImageId': 'ami-fa22a5ed',
#                 'KeyName': 'staging-factory',
#                 'SecurityGroups': [
#                     {
#                         'GroupId': 'sg-6bc31b13'
#                     },
#                 ],
#                 'InstanceType': instance_type[0],
#                 'BlockDeviceMappings': [
#                     {
#                         'DeviceName': "/dev/sda1",
#                         'Ebs': {
#                             'SnapshotId': 'snap-acba06b6',
#                             'VolumeSize': 25,
#                             'DeleteOnTermination': True,
#                             'VolumeType': 'gp2'
#                         },
#                     },
#                 ],
#                 'Monitoring': {
#                     'Enabled': False
#                 },
#                 'SubnetId': bid_subnet[0]
#             },
#         ]#,
#         #'AllocationStrategy': 'lowestPrice'
#     }
# )
#
# print sfir
#

sbir = ec2.request_spot_instances(
    SpotPrice=expected_bid_price_mapping[instance_type[0]],
    InstanceCount=1,
    ValidFrom=(end_time + timedelta(seconds=5)).strftime('%Y-%m-%dT%H:%M:%SZ'),
    ValidUntil=(end_time + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%SZ'),
    BlockDurationMinutes=request_duration,
    LaunchSpecification={
        'ImageId': 'ami-fa22a5ed',
        'KeyName': 'staging-factory',
        'InstanceType': instance_type[0],
        'BlockDeviceMappings': [
            {
                'DeviceName': "/dev/sda1",
                'Ebs': {
                    'SnapshotId': 'snap-acba06b6',
                    'VolumeSize': 25,
                    'DeleteOnTermination': True,
                    'VolumeType': 'gp2'
                },
            },
        ],
        'SubnetId': bid_subnet[0],
        'Monitoring': {
            'Enabled': False
        },
        'SecurityGroupIds': [
            'sg-6bc31b13',
        ]
    }
)

print sbir
