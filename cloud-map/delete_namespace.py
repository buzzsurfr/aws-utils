#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

__version__ = "0.1"

__author__ = "Theo Salvo"
__license__ = "Apache"
__maintainer__ = "Theo Salvo"
__url__ = "https://github.com/buzzsurfr/aws-utils"

# delete_namespace.py
#   Iterate through all of the resources of an AWS Cloud Map namespace and delete them, then delete namespace after

import os
import argparse
import boto3

parser = argparse.ArgumentParser()
parser.add_argument("--name", action="store", dest="namespace_name", required=True, help="Namespace Name")
parser.add_argument("--verbose", action="store_true", dest="verbose", help="Verbose")
args = parser.parse_args()

namespace_name = args.namespace_name
verbose = args.verbose

cloudmap = boto3.client('servicediscovery')

list_namespaces = cloudmap.list_namespaces()
if list_namespaces['ResponseMetadata']['HTTPStatusCode'] < 400:
    # Find namespace
    for namespace in list_namespaces['Namespaces']:
        if namespace['Name'] == namespace_name:
            # Services
            list_services = cloudmap.list_services(Filters=[{'Name': 'NAMESPACE_ID','Values':[namespace['Id']],'Condition': 'EQ'}])
            for service in list_services['Services']:
                # Service Instances
                list_instances = cloudmap.list_instances(ServiceId=service['Id'])

                for instance in list_instances['Instances']:
                    cloudmap.deregister_instance(ServiceId=service['Id'],InstanceId=instance['Id'])
                    if verbose:
                        print("Deregistered: " + instance['Id'] + ' from service '+ service['Name'])
                    
                cloudmap.delete_service(Id=service['Id'])
                if verbose:
                    print("Deleted: " + service['Name'] + ' (' + service['Arn'] + ')')

            cloudmap.delete_namespace(Id=namespace['Id'])
            print("Deleted: " + namespace['Name'] + ' (' + namespace['Arn'] + ')')
else:
    print("Could not find namespace "+namespace_name)
    os.exit(1)
