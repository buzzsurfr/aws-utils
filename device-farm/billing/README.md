# DeviceFarm-Billing

A process for providing detailed billing information about AWS DeviceFarm objects (projects, runs, etc).

## Instructions

This process will poll the Device Farm data monthly, store in S3, and allow for queries in Athena to generate the detailed billing information.

Because this is a polling solution, it's necessary to restrict access to the Device Farm Delete* APIs or the report may be inaccurate.

## Contents
* **etl-df-s3.py** - Python script that polls for DeviceFarm detailed run data and saves JSON documents to S3 bucket (specified as parameter).  Can be called as a Lambda function on a schedule (using CloudWatch Events).
* **create_table_runs.sql** - Presto SQL for creating database, table, and partitions in Athena.  Can be run from Athena console, but each query must be run separately.
* **queries.sql** - SQL for querying data from Athena.  Includes:
  * Device Time per project
  * Device Time per run per project
* **DeviceFarmFullAccessNoDelete-policy.json** - IAM policy for restricting Delete API commands in Device Farm.
* **ETL-DeviceFarmToS3Bucket-policy.json** - IAM policy used by script executor or lambda execution role.

## Setup

1. Clone the repository to your local computer.
1. In the *etl-df-s3.py* file, modify the s3_bucket. variable to include your destination bucket.
1. In the *ETL-DeviceFarmToS3Bucket-policy.json* file, modify the S3 ARN to use your destination bucket.
1. Import the ETL-DeviceFarmToS3Bucket and DeviceFarmFullAccessNoDelete policies (using the CreatePolicy API).
1. Run the *etl-df-s3.py* script locally or schedule as a Lambda function.
1. Open Athena and run each query found in *create_table_runs.sql* (Each query is delimited by comment "--").
1. In the Athena console, click "New Query".  Load the first query from the *queries.sql* file and click Save As.
1. Save the query using the header comments above the first query.
1. Repeat for every subsequent query in the *queries.sql* file.

## Use
1. From the [Athena console](https://console.aws.amazon.com/athena/home), click on "Saved Queries".
1. Click on one of the saved queries.  For example, "DF Billing/Proj (Last Month)"
1. Click Run Query.  The query will run in the background and display results under the query.
You can download the results by clicking on the Download button in the top-right corner.  Results are also automatically saved to the Athena S3 bucket.
