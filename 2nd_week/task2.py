import argparse
import boto3
from botocore.exceptions import ClientError
import json
from os import getenv
import logging


def check_bucket_policy(s3_client, bucket_name):
  try:
    response = s3_client.get_bucket_policy(Bucket=bucket_name)
    policy = response['Policy']
    return policy
  except ClientError as e:
    if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
      return None
    else:
      print(f"Error checking bucket policy: {e}")
      return None


def create_bucket_policy(s3_client, bucket_name):
  policy = {
      "Version":
      "2012-10-17",
      "Statement": [{
          "Effect": "Allow",
          "Principal": "*",
          "Action": "s3:GetObject",
          "Resource": f"arn:aws:s3:::{bucket_name}/dev/*"
      }, {
          "Effect": "Allow",
          "Principal": "*",
          "Action": "s3:GetObject",
          "Resource": f"arn:aws:s3:::{bucket_name}/test/*"
      }]
  }
  try:
    policy_json = json.dumps(policy)
    s3_client.put_bucket_policy(Bucket=bucket_name, Policy=policy_json)
    print("Bucket policy created successfully.")
  except ClientError as e:
    print(f"Error creating bucket policy: {e}")


def init_client():
  try:
    client = boto3.client(
        "s3",
        aws_access_key_id=getenv("aws_access_key_id"),
        aws_secret_access_key=getenv("aws_secret_access_key"),
        aws_session_token=getenv("aws_session_token"),
        region_name=getenv("aws_region_name"))
    client.list_buckets()
    return client
  except ClientError as e:
    logging.error(e)
  except:
    logging.error("Unexpected Error")


def main():
  parser = argparse.ArgumentParser(
      description="Check or create an S3 bucket policy.")
  parser.add_argument("bucket_name", type=str, help="Name of the S3 bucket")
  args = parser.parse_args()

  bucket_name = args.bucket_name

  s3_client = boto3.client('s3')

  existing_policy = check_bucket_policy(s3_client, bucket_name)
  if existing_policy:
    print("Bucket policy already exists:")
    print(existing_policy)
  else:
    create_bucket_policy(s3_client, bucket_name)


if __name__ == "__main__":
  main()
