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

appmesh = boto3.client('appmesh')

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

