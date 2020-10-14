#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

__version__ = "0.1"

__author__ = "Theo Salvo"
__license__ = "Apache"
__maintainer__ = "Theo Salvo"
__url__ = "https://github.com/buzzsurfr/aws-utils"

# list_mesh_contents.py
#   Iterate through all of the resources of an AWS App Mesh and output to terminal

import boto3

appmesh = boto3.client('appmesh-preview', region_name='us-west-2')

for mesh in appmesh.list_meshes()['meshes']:
    print(mesh['arn'])
    # Nodes
    for node in appmesh.list_virtual_nodes(meshName=mesh['meshName'])['virtualNodes']:
        print(node['arn'])

    # Routers
    for router in appmesh.list_virtual_routers(meshName=mesh['meshName'])['virtualRouters']:
        print(router['arn'])
        # Routes
        for route in appmesh.list_routes(meshName=mesh['meshName'],virtualRouterName=router['virtualRouterName'])['routes']:
            print(route['arn'])

    # Services
    for service in appmesh.list_virtual_services(meshName=mesh['meshName'])['virtualServices']:
        print(service['arn'])

    # Gateways
    for gateway in appmesh.list_virtual_gateways(meshName=mesh['meshName'])['virtualGateways']:
        print(gateway['arn'])
        # Gateway Routes
        for gateway_route in appmesh.list_gateway_routes(meshName=mesh['meshName'],virtualGatewayName=gateway['virtualGatewayName'])['gatewayRoutes']:
            print(gateway_route['arn'])
