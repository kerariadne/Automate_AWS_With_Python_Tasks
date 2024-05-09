import argparse
import boto3
from botocore.exceptions import ClientError
import logging
from os import getenv
from dotenv import load_dotenv

def create_bucket(aws_s3_client, bucket_name, region='us-west-2'):
    try:
        location = {'LocationConstraint': region}
        aws_s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
        print(f"Bucket '{bucket_name}' created successfully.")
    except ClientError as e:
        logging.error(f"Failed to create bucket '{bucket_name}': {e}")
        return False
    return True

def bucket_exists(aws_s3_client, bucket_name):
    try:
        aws_s3_client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            logging.error(f"Error checking bucket '{bucket_name}': {e}")
            return False

def init_client():
    try:
        client = boto3.client(
            "s3",
            aws_access_key_id=getenv("aws_access_key_id"),
            aws_secret_access_key=getenv("aws_secret_access_key"),
            aws_session_token=getenv("aws_session_token"),
            region_name=getenv("aws_region_name")
        )
        client.list_buckets()
        return client
    except ClientError as e:
        logging.error(f"Failed to initialize S3 client: {e}")
        return None

if __name__ == "__main__":
    load_dotenv()  
    s3_client = init_client()

    parser = argparse.ArgumentParser(description="Check or create an S3 bucket.")
    parser.add_argument("bucket_name", type=str, help="Name of the S3 bucket")
    args = parser.parse_args()

    bucket_name = args.bucket_name

    if bucket_exists(s3_client, bucket_name):
        print(f"Bucket '{bucket_name}' already exists.")
    else:
        create_bucket(s3_client, bucket_name)
