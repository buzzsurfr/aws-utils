#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

__version__ = "0.2"

__author__ = "Theo Salvo"
__license__ = "Apache"
__maintainer__ = "Theo Salvo"
__url__ = "https://github.com/buzzsurfr/aws-utils"

import os
import time
import argparse
import boto3

parser = argparse.ArgumentParser()
parser.add_argument("--profile", action="store", dest="profile", default="default", help="Local profile")
parser.add_argument("--verbose", action="store_true", dest="verbose", help="Verbose")
parser.add_argument("--checkpoint", action="store", type=int, dest="checkpoint", default=10, help="Check in every ## topics")
args = parser.parse_args()

if args.verbose:
    print("Using profile " + args.profile)

#  Initialize client (potentially using old access key)
if args.verbose:
    print("Connecting to SNS...")
session = boto3.Session(profile_name=args.profile)
sns = session.resource("sns")

counter = 0
if args.verbose:
    print("Counting topics", end="")

for topic in sns.topics.all():
    counter = counter + 1
    if args.verbose and counter % args.checkpoint == 0:
        print(".", end="")
print("done")

print("Topics: " + str(counter))
