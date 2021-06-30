#!/usr/bin/env python
import boto3
import json
import datetime
import calendar

s3_bucket = "devicefarm-billing"

class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            try:
                return calendar.timegm(obj.utctimetuple())
            except TypeError:
                return str(obj)
        else:
            return str(obj)

def handler(event, context):
    df = boto3.client("devicefarm", region_name="us-west-2")
    s3 = boto3.client("s3")

    #  Get list of projects from DeviceFarm
    projects = df.list_projects()['projects']

    for project in projects:

        #  Get runs per project
        runs = df.list_runs(arn=project['arn'])['runs']

        for run in runs:
            #  Add project data to run struct
            run['project'] = project
            #  Create bucket key for objects
            #  Format: {{year}} / {{month}} / {{project}} / {{run}}
            s3_key = "year=" + str(run['created'].year) + "/" + "month=" + str(run['created'].month) + "/" + run['arn'].split(':')[-1]

            #  Save run as JSON document in S3
            resp = s3.put_object(Bucket=s3_bucket,Key=s3_key,Body=json.dumps(run, cls=DatetimeEncoder))

if __name__ == "__main__":
    handler("","")
