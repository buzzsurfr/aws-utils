#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

__version__ = "0.1"

__author__ = "Theo Salvo"
__license__ = "Apache"
__maintainer__ = "Theo Salvo"
__url__ = "https://github.com/buzzsurfr/aws-utils"

# delete_mesh.py
#   Iterate through all of the resources of an AWS App Mesh and delete them, then delete mesh after

import sys
import argparse
import boto3

parser = argparse.ArgumentParser()
parser.add_argument("--name", action="store", dest="mesh_name", required=True, help="Mesh Name")
parser.add_argument("--verbose", action="store_true", dest="verbose", help="Verbose")
args = parser.parse_args()

mesh_name = args.mesh_name
verbose = args.verbose

appmesh = boto3.client('appmesh')

describe_mesh = appmesh.describe_mesh(meshName=mesh_name)
if describe_mesh['ResponseMetadata']['HTTPStatusCode'] < 400:
    # Gateways
    for gateway in appmesh.list_virtual_gateways(meshName=mesh_name)['virtualGateways']:
        # Gateway Routes
        for gateway_route in appmesh.list_gateway_routes(meshName=mesh_name,virtualGatewayName=gateway['virtualGatewayName'])['gatewayRoutes']:
            appmesh.delete_gateway_route(meshName=mesh_name,virtualGatewayName=gateway['virtualGatewayName'], gatewayRouteName=gateway_route['gatewayRouteName'])
            if verbose:
                print("Deleted: " + gateway_route['arn'])
        appmesh.delete_virtual_gateway(meshName=mesh_name,virtualGatewayName=gateway['virtualGatewayName'])
        if verbose:
            print("Deleted: " + gateway['arn'])

    # Services
    for service in appmesh.list_virtual_services(meshName=mesh_name)['virtualServices']:
        appmesh.delete_virtual_service(meshName=mesh_name,virtualServiceName=service['virtualServiceName'])
        if verbose:
            print("Deleted: " + service['arn'])

    # Routers
    for router in appmesh.list_virtual_routers(meshName=mesh_name)['virtualRouters']:
        # Routes
        for route in appmesh.list_routes(meshName=mesh_name,virtualRouterName=router['virtualRouterName'])['routes']:
            appmesh.delete_route(meshName=mesh_name,virtualRouterName=router['virtualRouterName'], routeName=route['routeName'])
            if verbose:
                print("Deleted: " + route['arn'])
        appmesh.delete_virtual_router(meshName=mesh_name,virtualRouterName=router['virtualRouterName'])
        if verbose:
            print("Deleted: " + router['arn'])

    # Nodes
    for node in appmesh.list_virtual_nodes(meshName=mesh_name)['virtualNodes']:
        appmesh.delete_virtual_node(meshName=mesh_name,virtualNodeName=node['virtualNodeName'])
        if verbose:
            print("Deleted: " + node['arn'])

    appmesh.delete_mesh(meshName=mesh_name)
    print("Deleted: " + describe_mesh['mesh']['metadata']['arn'])
else:
    print("Could not find mesh "+mesh_name)
    sys.exit(1)
