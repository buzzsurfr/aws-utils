# aws-utils
Utilities and Scripts for Amazon Web Services (AWS)

## By Service

* App Mesh
  * [list_mesh_contents.py](appmesh_list_mesh_contents/) - Iterate through all of the resources of an AWS App Mesh and output to terminal
* Elastic Compute Cloud (EC2)
  * [get_instance_limits.py](ec2_get_instance_limits/) - Get the EC2 instance per-type limits in a serialized format
* Identity and Access Management (IAM)
  * [rotate_access_key.py](iam_rotate_access_key/) - Automatically rotates the oldest AWS Access Key locally. Optionally specify a profile to change the key for that profile.
  * iam-key-rotation.py:
    1. Automatically rotates the oldest AWS access key locally.
    2. Mandatory parameters to be passed are --username & --profile while executing this script. E.g If AWS IAM username is bob and aws cli profile in local system for bob          credentials is default, then script will be executed by passing these parameters. ( python3 iam-key-rotation.py --username bob --profile default.
    3. Pre-requisities to use this script: aws cli & python3. 
    4. To aiutomate it further, a cronjob may be used in Linux or macos to execute this python scriopt on a daily basis.
* Simple Notification Service (SNS)
  * [count_topics.py](sns_count_topics/) - Counts the number of SNS topics in an account/region. Uses pagination to scale to SNS Topic Limit, and includes a "checkpoint" to track progress.
* Systems Manager (SSM)
  * [get_all_parameters.py](ssm_get_all_parameters/) - Batch operation to return all parameters. Profile aware, and has a flag for decryption.
