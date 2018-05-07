#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "1.0.1"

__author__ = "Theo Salvo"
__license__ = "Apache"
__maintainer__ = "Theo Salvo"
__url__ = "https://github.com/buzzsurfr/aws-utils"

# rotate_access_key.py
#   Automatically rotates the oldest AWS Access Key locally. Optionally specify a profile to change the key for that profile.
#   Based on https://aws.amazon.com/blogs/security/how-to-rotate-access-keys-for-iam-users/

import os
import argparse
import boto3

parser = argparse.ArgumentParser()
parser.add_argument("--user-name", action="store", dest="user_name", required=True, help="UserName of the AWS user")
parser.add_argument("--access-key-id", action="store", dest="access_key_id", help="Specific Access Key to replace")
parser.add_argument("--profile", action="store", dest="profile", help="Local profile")
parser.add_argument("--delete", action="store_true", dest="delete_access_key", default=True, help="Delete old access key after inactivating (Default)")
parser.add_argument("--no-delete", action="store_false", dest="delete_access_key", help="Do not delete old access key after inactivating")
parser.add_argument("--verbose", action="store_true", dest="verbose", help="Verbose")
args = parser.parse_args()

user_name = args.user_name

#  Initialize client (potentially using old access key)
if args.verbose:
    print "Connecting to IAM..."
session = boto3.Session(profile_name=args.profile)
iam = session.client("iam")

#  Get current access keys for specified user
#  Command: aws iam list-access-keys --user-name {{AWS:UserName}}
#  **FUTURE** add try/catch logic
access_keys = iam.list_access_keys(UserName=user_name)["AccessKeyMetadata"]
if access_keys:
    access_keys.sort(key=lambda r: r["CreateDate"])
if args.access_key_id and access_keys and args.access_key_id in [ak["AccessKeyId"] for ak in access_keys]:
    access_key_id = args.access_key_id
    if args.verbose:
        print "Using access key (%s)..." % access_key_id
elif not access_keys:
    access_key_id = None
    if args.verbose:
        print "No current access keys..."
elif len(access_keys) == 1:
    access_key_id = access_keys[0]["AccessKeyId"]
    if args.verbose:
        print "Using access key (%s)..." % access_key_id
else:
    #  More than one access key present, choose
    #  Handle multiple access keys for this user, potentially sorting by oldest created
    #  Assign to variables user_name and access_key_id
    access_keys.sort(key=lambda r: r["CreateDate"])
    access_key_id = access_keys[0]["AccessKeyId"]
    if args.verbose:
        print "Using oldest access key (%s) in rotation..." % access_key_id

#  Create new access key for specified user
#  Command: aws iam create-access-key --user-name {{AWS:UserName}}
#  **FUTURE** add try/catch logic
if args.verbose:
    print "Creating new access key..."
new_access_key = iam.create_access_key(UserName=user_name)["AccessKey"]

#  Locally configure new access key, replacing old key
#  Command: aws configure
#  **FUTURE** add support for profile
#  **FUTURE** accept credentials file as argument
if args.verbose:
    print "Rotating access key locally..."
os.system("aws --profile="+args.profile+" configure set aws_access_key_id "+new_access_key["AccessKeyId"])
os.system("aws --profile="+args.profile+" configure set aws_secret_access_key "+new_access_key["SecretAccessKey"])

#  Re-establish IAM connection using new credentials
del iam
if args.verbose:
    print "Reconnecting to IAM using new access key..."
session = boto3.Session(profile_name=args.profile)
iam = session.client("iam")

#  Make old access key inactive (if old existed)
#  Command: aws iam update-access-key --access-key-id AKIA**************** --user-name {{AWS:UserName}} --status Inactive
#  **FUTURE** add try/catch logic
if access_key_id:
    if args.verbose:
        print "Inactivating old access key..."
    iam.update_access_key(AccessKeyId=access_key_id, UserName=user_name, Status="Inactive")

    #  Delete old access key (based on Argument)
    #  Default: True
    #  Command: aws iam delete-access-key --access-key-id AKIA**************** --user-name {{AWS:UserName}}
    #  **FUTURE** add try/catch logic
    if args.delete_access_key:
        if args.verbose:
            print "Deleting old access key..."
        iam.delete_access_key(AccessKeyId=access_key_id, UserName=user_name)
