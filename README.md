# aws-utils
Utilities and Scripts for Amazon Web Services (AWS)

## By Service

* Elastic Compute Cloud (EC2)
  * [get_instance_limits.py](ec2_get_instance_limits/) - Get the EC2 instance per-type limits in a serialized format
* Identity and Access Management (IAM)
  * [rotate_access_key.py](iam_rotate_access_key/) - Automatically rotates the oldest AWS Access Key locally. Optionally specify a profile to change the key for that profile.
* Simple Notification Service (SNS)
  * [count_topics.py](sns_count_topics/) - Counts the number of SNS topics in an account/region. Uses pagination to scale to SNS Topic Limit, and includes a "checkpoint" to track progress.