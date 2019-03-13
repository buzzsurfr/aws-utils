#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

__version__ = "0.1"

__author__ = "Theo Salvo"
__license__ = "Apache"
__maintainer__ = "Theo Salvo"
__url__ = "https://github.com/buzzsurfr/aws-utils"

# get_all_parameters.py
#   Batch operation to return all parameters. Profile aware, and has a flag for decryption

import os
import time
import json
import datetime
import argparse
import boto3

def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

parser = argparse.ArgumentParser()
parser.add_argument("--profile", action="store", dest="profile", default="default", help="Local profile")
parser.add_argument("--verbose", action="store_true", dest="verbose", help="Verbose")
parser.add_argument("--with-decryption", action="store_true", dest="with_decryption", default=False, help="Decrypt the values")
args = parser.parse_args()

if args.verbose:
    print("Using profile " + args.profile)
    if args.with_decryption:
        print("with Decryption")

#  Initialize client (potentially using old access key)
if args.verbose:
    print("Connecting to SNS...")
session = boto3.Session(profile_name=args.profile)
ssm = session.client("ssm")

# Get Parameter Names (DescribeParameters API)
dp_result = ssm.describe_parameters()
if 'Parameters' in dp_result:
    parameter_names = [param['Name'] for param in dp_result['Parameters']]
while 'NextToken' in dp_result:
    next_token = dp_result['NextToken']
    dp_result = ssm.describe_parameters(NextToken=next_token)
    if 'Parameters' in dp_result:
        parameter_names.extend([param['Name'] for param in dp_result['Parameters']])

# Get Parameter Values (GetParameters API)
#   Must batch in groups of 10
GP_BATCH_SIZE = 10
param_chunks = [parameter_names[i * GP_BATCH_SIZE:(i + 1) * GP_BATCH_SIZE] for i in range((len(parameter_names) + GP_BATCH_SIZE - 1) // GP_BATCH_SIZE )]
parameter_values = []
for pc in param_chunks:
    gp_result = ssm.get_parameters(Names=pc,WithDecryption=args.with_decryption)
    if 'Parameters' in gp_result:
        parameter_values.extend(gp_result['Parameters'])

print(json.dumps(parameter_values, default=default))