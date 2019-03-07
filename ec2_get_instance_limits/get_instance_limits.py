#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

__version__ = "0.2"

__author__ = "Theo Salvo"
__license__ = "Apache"
__maintainer__ = "Theo Salvo"
__url__ = "https://github.com/buzzsurfr/aws-utils"

# get_instance_limits.py
#   Get the EC2 instance per-type limits in a serialized format

import os
import sys
import time
import logging
import json
import argparse
import boto3

parser = argparse.ArgumentParser()
parser.add_argument("--language-code", action="store", dest="language_code", default="en", choices=['en', 'jp'], help="Language Code")
parser.add_argument("--check-id", action="store", dest="check_id", default="0Xc6LMYG8P", help="TA Check ID")
parser.add_argument("--profile", action="store", dest="profile", default="default", help="Local profile")
parser.add_argument("--refresh", action="store_true", dest="refresh_check", default=False, help="Refresh the Trusted Advisor check before getting instance limits")
parser.add_argument("--wait", action="store_true", dest="refresh_wait", default=False, help="Whether to wait on the refresh window to refresh the status")
parser.add_argument("--verbose", action="store_true", dest="verbose", help="Verbose")
args = parser.parse_args()

logger = logging.getLogger()
if args.verbose:
    logger.setLevel(logging.DEBUG)

#  Initialize client
logger.debug("Connecting to Support API...")
session = boto3.Session(profile_name=args.profile, region_name="us-east-1")
support = session.client('support')

# Refresh if selected
if args.refresh_check:
    check_status = support.describe_trusted_advisor_check_refresh_statuses(checkIds=[args.check_id])['statuses'][0]
    if check_status['millisUntilNextRefreshable'] > 0:
        if args.refresh_wait:
            logger.warning("Check is ineligible for refresh (may have been refreshed recently). Waiting " + str(check_status['millisUntilNextRefreshable']/1000+1) + " seconds before continuing.")
            time.sleep(check_status['millisUntilNextRefreshable']/1000+1)
        else:
            logger.warning("Check is ineligible for refresh (may have been refreshed recently). Continuing...")
    refresh_result = support.refresh_trusted_advisor_check(checkId=args.check_id)
    if refresh_result['status']['status'] not in ('success','none'):
        logger.warning("Status is refreshing. You may need to run again.")
    elif refresh_result['ResponseMetadata']['HTTPStatusCode'] >= 400:
        logger.warning("Unable to refresh. Continuing...")

# Get Metadata headers from checkId
check_metadata = []
ta_checks = support.describe_trusted_advisor_checks(language=args.language_code)

if 'checks' not in ta_checks:
    sys.exit("Error with calling support:DescribeTrustedAdvisorChecks API")

for check in ta_checks['checks']:
    if check['id'] == args.check_id:
        check_metadata = check['metadata']

# Check EC2 limits
ec2_limits_check = support.describe_trusted_advisor_check_result(checkId="0Xc6LMYG8P")

if 'result' not in ec2_limits_check:
    sys.exit("Error with calling support:DescribeTrustedAdvisorCheckResult API")

ec2_limits = []
for flaggedResource in ec2_limits_check['result']['flaggedResources']:
    limit = {}
    for key in range(len(check_metadata)):
        if check_metadata[key] == "Limit Name":
            limit["Instance Type"] = flaggedResource['metadata'][key].replace('On-Demand instances - ','')
        else:
            limit[check_metadata[key]] = flaggedResource['metadata'][key]
    ec2_limits.append(limit)

print(json.dumps(ec2_limits))