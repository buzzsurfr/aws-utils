#!/usr/bin/env python
#
# iam_policy_summary.py
#
#  Show a summary format per user similar to the Policy Summary

import json
import copy
import csv
import time
import boto3
import pprint

# Load Data from file
# json_data = open("iam.json", "r").read()
# data = json.loads(json_data)
# policies = data['Policies']

# Load data from AWS API call iam:GetAccountAuthorizationDetails
iam = boto3.client('iam')
data = {
    'RoleDetailList': [],
    'GroupDetailList': [],
    'UserDetailList': [],
    'Policies': []
}
result = iam.get_account_authorization_details()
data['RoleDetailList'] += result['RoleDetailList']
data['GroupDetailList'] += result['GroupDetailList']
data['UserDetailList'] += result['UserDetailList']
data['Policies'] += result['Policies']
while result['IsTruncated']:
    marker = result['Marker']
    result = iam.get_account_authorization_details(Marker=marker)
    data['RoleDetailList'] += result['RoleDetailList']
    data['GroupDetailList'] += result['GroupDetailList']
    data['UserDetailList'] += result['UserDetailList']
    data['Policies'] += result['Policies']

policies = data['Policies']

for policy in policies:
# Add to record and return:
#
# "summary": [
#     {
#         "service": "$service_name",
#         "permission": "read" | "write"
#     },
#     ...
# ]
#
    summary = []

    # print "Policy: ", policy['PolicyName']
    for policy_version in policy['PolicyVersionList']:
        # print "Policy Version: ", policy_version['VersionId']
        if policy_version['IsDefaultVersion']:
            for statement in policy_version['Document']['Statement']:
                # print "Statement: ", statement
                if statement['Effect'] == 'Allow':
                    if isinstance(statement['Action'], basestring):
                        if statement['Action'] == '*':
                            summary += [
                                {
                                    "service": '*',
                                    "permission": "read"
                                },
                                {
                                    "service": '*',
                                    "permission": "write"
                                }
                            ]
                        else:
                            # print "Action: ", action
                            service, command = statement['Action'].split(':')
                            if command.startswith('Describe') or command.startswith('List') or command.startswith('Get'):
                                summary.append({
                                    "service": service,
                                    "permission": "read"
                                })
                            else:
                                summary.append({
                                    "service": service,
                                    "permission": "write"
                                })
                    else:
                        for action in statement['Action']:
                            if action == '*':
                                summary += [
                                    {
                                        "service": '*',
                                        "permission": "read"
                                    },
                                    {
                                        "service": '*',
                                        "permission": "write"
                                    }
                                ]
                            else:
                                # print "Action: ", action
                                service, command = action.split(':')
                                if command.startswith('Describe') or command.startswith('List') or command.startswith('Get'):
                                    summary.append({
                                        "service": service,
                                        "permission": "read"
                                    })
                                else:
                                    summary.append({
                                        "service": service,
                                        "permission": "write"
                                    })
    policy['summary'] = [dict(t) for t in set([tuple(d.items()) for d in summary])]
    # policy['summary'] = summary

# Aggregate group policies to user
for user in data['UserDetailList']:
    # Add user policies to summary
    map(lambda x: x.update({"GroupName": ""}), user['AttachedManagedPolicies'])

    # Add group policies to summary
    for group in data['GroupDetailList']:
        if group['GroupName'] in user['GroupList']:
            group_policies = copy.deepcopy(group['AttachedManagedPolicies'])
            map(lambda x: x.update({"GroupName": group['GroupName']}), group_policies)
            user['AttachedManagedPolicies'] += group_policies

# Enrich and aggregate policy summary to user based on policies
for user in data['UserDetailList']:
    summary = []

    # policy_arns = [policy['PolicyArn'] for policy in user['AttachedManagedPolicies']]
    policy_arns = {policy['Arn']: policy for policy in policies}

    for policy in user['AttachedManagedPolicies']:
        if policy['PolicyArn'] in policy_arns.keys():
            policy_summary = copy.deepcopy(policy_arns[policy['PolicyArn']]['summary'])
            for p in policy_summary:
                p.update({'GroupName': policy['GroupName']})
            summary += copy.deepcopy(policy_summary)
    # for policy in policies:
    #     if policy['Arn'] in policy_arns:
    #         # print "PolicyArn: ", policy['Arn']
    #         summary += copy.deepcopy(policy['summary'])

    # print("User:")
    # pprint.pprint(user)
    # print("Summary:")
    # pprint.pprint(summary)
    user['summary'] = [dict(t) for t in set([tuple(d.items()) for d in summary])]

# Export to CSV
with open('policy_summary_'+time.strftime("%Y%m%dT%H%M%S")+'.csv','w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['UserName', 'GroupName', 'Service', 'Permission'])
    writer.writeheader()

    for user in data['UserDetailList']:
        for summary in user['summary']:
            writer.writerow({'UserName': user['UserName'], 'GroupName': summary['GroupName'], 'Service': summary['service'], 'Permission': summary['permission']})
