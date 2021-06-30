-- Create Database
CREATE DATABASE IF NOT EXISTS billing_devicefarm;

-- Create Table
CREATE EXTERNAL TABLE IF NOT EXISTS runs (
  status STRING,
  name STRING,
  created TIMESTAMP,
  totalJobs INT,
  completedJobs INT,
  deviceMinutes STRUCT<
    unmetered:DOUBLE,
    total:DOUBLE,
    metered:DOUBLE >,
  platform STRING,
  result STRING,
  billingMethod STRING,
  type STRING,
  arn STRING,
  project STRUCT<
    name:STRING,
    arn:STRING,
    created:TIMESTAMP >,
  counters STRUCT<
    skipped:INT,
    warned:INT,
    failed:INT,
    stopped:INT,
    passed:INT,
    errored:INT,
    total:INT >
)
PARTITIONED BY (
  year INT,
  month INT
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES (
  "timestamp.formats"="yyyy-MM-dd'T'HH:mm:ss.millis"
)
LOCATION 's3://devicefarm-billing/'

-- Rebuild partitions
MSCK REPAIR TABLE billing_devicefarm
