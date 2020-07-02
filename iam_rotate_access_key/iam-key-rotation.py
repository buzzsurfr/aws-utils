import boto3
from argparse import ArgumentParser
from os import system
from time import sleep

parse = ArgumentParser()
parse.add_argument("--username", required=True, help="Enter AWS IAM user whose IAM key has to be rotated")
parse.add_argument("--profile", required=True, help="AWS cli profile whose IAM keys has to be rotated")

args = parse.parse_args()
username = args.username
profile = args.profile

print("Connecting AWS IAM service-->")
session = boto3.Session(profile_name=profile)
key_rotation_session = session.client("iam")

current_access_keys = key_rotation_session.list_access_keys(UserName=username)["AccessKeyMetadata"]

if len(current_access_keys) == 1:
    old_access_key = current_access_keys[0]["AccessKeyId"]
    print("Current IAM access key will be rotated-->")

else:
    current_access_keys.sort(key=lambda r: r["CreateDate"])
    old_access_key = current_access_keys[0]["AccessKeyId"]
    print("Old IAM access key will be rotated-->")

print("Generating new IAM access key-->")
new_access_key = key_rotation_session.create_access_key(UserName=username)["AccessKey"]
print("Replacing current IAM access key with the new one. Wait for few seconds...")

a = new_access_key["AccessKeyId"]
b = new_access_key["SecretAccessKey"]
system("aws configure set aws_access_key_id " + str(a) + " --profile " + str(profile))
system("aws configure set aws_secret_access_key " + str(b) + " --profile " + str(profile))

sleep(10)

del key_rotation_session
print("Reconnecting to IAM using new access key-->")
session = boto3.Session(profile_name=profile)
key_rotation_session = session.client("iam")

print("Deactivating old IAM access key-->")
key_rotation_session.update_access_key(AccessKeyId=old_access_key, UserName=username, Status="Inactive")

print("Deleting old IAM access key-->")
key_rotation_session.delete_access_key(AccessKeyId=old_access_key, UserName=username)

print("IAM access keys rotated.")






