import argparse
import boto3
from botocore.exceptions import ClientError
import logging
from os import getenv
from dotenv import load_dotenv

load_dotenv()


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


def delete_bucket(aws_s3_client, bucket_name):
  try:
    aws_s3_client.delete_bucket(Bucket=bucket_name)
  except ClientError as e:
    logging.error(e)
    return False
  return True


def bucket_exists(aws_s3_client, bucket_name):
  try:
    response = aws_s3_client.head_bucket(Bucket=bucket_name)
  except ClientError as e:
    logging.error(e)
    return False
  status_code = response["ResponseMetadata"]["HTTPStatusCode"]
  if status_code == 200:
    return True
  return False


if __name__ == "__main__":
  load_dotenv()
  s3_client = init_client()

  parser = argparse.ArgumentParser(description="Check and delete an S3 bucket.")
  parser.add_argument("bucket_name", type=str, help="Name of the S3 bucket")
  args = parser.parse_args()

  bucket_name = args.bucket_name

  if bucket_exists(s3_client, bucket_name):
    delete_bucket(s3_client, bucket_name)
  else:
    print(f"Bucket '{bucket_name}' does not exist.")
