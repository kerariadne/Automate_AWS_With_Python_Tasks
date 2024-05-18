from pathlib import Path
import boto3
from os import getenv
from dotenv import load_dotenv
import logging
from botocore.exceptions import ClientError
from hashlib import md5
from time import localtime
import argparse
from urllib.request import urlopen
import io
import pylibmagic 
import magic

load_dotenv()

parser = argparse.ArgumentParser(description="This code helps with buckets")
parser.add_argument('bucketname', help="bucket name", type=str)
parser.add_argument('-o', '--objectName', help="object name", type=str, required=False)
parser.add_argument('-u', '--url', help="url to upload it on bucket", type=str, required=False)
parser.add_argument('-kl', '--keep_local', help="flag to check keep local", type=str, required=False, default=False, nargs="?", const=True)
parser.add_argument("-cb","--createbucket", help="Flag to create bucket.", choices=["False", "True"], type=str, nargs="?", const="True", default="False")
parser.add_argument("-db","--deletebucket", help="Flag to delete bucket.", choices=["False", "True"], type=str, nargs="?", const="True", default="False")
parser.add_argument("-be","--bucketexists", help="Flag to check bucket existing", choices=["False", "True"], type=str, nargs="?", const="True", default="False")
parser.add_argument("-dau","--download_upload_file", help="Flag to download file and upload to s3", choices=["False", "True"], type=str, nargs="?", const="True", default="False")
parser.add_argument("-cbp","--create_bucket_policy", help="Flag to create bucket policy", choices=["False", "True"], type=str, nargs="?", const="True", default="False")
parser.add_argument("-rbp","--read_bucket_policy", help="Flag to check bucket policy", choices=["False", "True"], type=str, nargs="?", const="True", default="False")
parser.add_argument("-soap","--set_object_access_policy", help="Flag to set_object_access_policy", choices=["False", "True"], type=str, nargs="?", const="True", default="False")


args = parser.parse_args()

def init_client():
    try:
        client = boto3.client("s3",
                              aws_access_key_id=getenv("aws_access_key_id"),
                              aws_secret_access_key=getenv("aws_secret_access_key"),
                              aws_session_token=getenv("aws_session_token"),
                              region_name=getenv("aws_region_name")) 
        print(client.list_buckets())
        return client
    except ClientError as e:
        logging.error(e)
    except:
        logging.error("Unexpected error")
 
 
def list_buckets(aws_s3_client):
    try:
        return aws_s3_client.list_buckets()
    except ClientError as e:
        logging.error(e)
        return False
 
 
def create_bucket(aws_s3_client, bucket_name, region=getenv("aws_region_name")):
    if (bucket_exists(bucket_name)):
        print(f"\nBucket '{bucket_name}' already exists\n")
        return False
    try:
        location = {'LocationConstraint': region}
        response = aws_s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration=location
        )
    except ClientError as e:
        logging.error(e)
        return False
    status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if status_code == 200:
        return True
    return False
 
 
def delete_bucket(aws_s3_client, bucket_name):
    try:
        response = aws_s3_client.delete_bucket(Bucket=bucket_name)
    except ClientError as e:
        logging.error(e)
        return False
    status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    
    if status_code == 204:
        return True
    return False
 
 
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
 
 

def download_file_and_upload_to_s3(aws_s3_client, bucket_name, url, keep_local=False):
    content_types = {'bmp': 'image/bmp', 
                     'jpg': 'image/jpeg', 
                     'jpeg': 'image/jpeg',
                     'png': 'image/png',
                     'webp': 'video/webm',
                     'mp4': 'video/mp4',
                     }
    with urlopen(url) as url:
        content = url.read()
        mime_type = magic.from_buffer(url, mime=True) # image/jpg
        for key, value in content_types:
            if value == mime_type:
                content_type = mime_type
                file_extension = key
                file_name = f'up_{md5(str(localtime()).encode("utf-8")).hexdigest()}.{file_extension}'

    try:
        aws_s3_client.upload_fileobj(
            Fileobj=io.BytesIO(content),
            Bucket=bucket_name,
            ExtraArgs={'ContentType': content_type},
            Key = file_name
            )
        
    except Exception as e:
        logging.error(e)
 
    # lokalurad shenaxva
    if keep_local:
        with open(Path(f"download/{file_name}"), mode="wb") as file:
            file.write(content)
 

    return "https://s3-{0}.amazonaws.com/{1}/{2}".format(
        'us-west-2',
        bucket_name,
        file_name
    )
 

# put_object_acl - Applies an access control policy  ACL to an Amazon S3 object
def set_object_access_policy(aws_s3_client, bucket_name, file_name):
    aws_s3_client.put_bucket_ownership_controls(
      Bucket=bucket_name,
      OwnershipControls={'Rules': [{
          'ObjectOwnership': 'ObjectWriter'
    }]})
    
    try:
        response = aws_s3_client.put_object_acl(
            ACL="public-read",
            Bucket=bucket_name,
            Key=file_name
        )
    except ClientError as e:
        logging.error(e)
        return False
    status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if status_code == 200:
        return True
    return False
 

def generate_policy(bucket_name):
    policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*"
        }
        ]
    }

    import json
    policy = json.dumps(policy)
    return policy

# put_bucket_policy - Applies S3 bucket policy to an Amazon S3 bucket
def create_bucket_policy(aws_s3_client, bucket_name):
    aws_s3_client.delete_public_access_block(Bucket=bucket_name)
    aws_s3_client.put_bucket_policy(
        Bucket=bucket_name, Policy=generate_policy(bucket_name)
        )
    print("Bucket policy created successfully")


# get_bucket_policy - Retrieves the policy for the specified bucket
def read_bucket_policy(aws_s3_client, bucket_name):
    try:
        policy = aws_s3_client.get_bucket_policy(Bucket=bucket_name)
        policy_str = policy["Policy"]
        print(policy_str)
    except ClientError as e:
        logging.error(e)
        return False
 

def main():
    s3_client = init_client()

    if args.createbucket == "True":
        print(args.bucketname)
        if create_bucket(s3_client, args.bucketname, "us-west-2"):
            print("bucket created!")
        else:
            print("bucket is not created!")

    if args.deletebucket == "True":
        if delete_bucket(s3_client, args.bucketname):
            print("bucket deleted successfully!")
        else:
            print("bucket is not deleted!")

    if args.bucketexists == "True":
        if bucket_exists(s3_client, args.bucketname):
            print(f"{args.bucketname} bucket exists!")
        else:
            print(f"{args.bucketname} bucket does not exist!")

    if args.create_bucket_policy == "True":
        create_bucket_policy(s3_client, args.bucketname)
    
    if args.read_bucket_policy == "True":
        read_bucket_policy(s3_client, args.bucketname)

    if args.set_object_access_policy == "True":
        if args.objectName is not None:
            print(f"set read status: {set_object_access_policy(s3_client, args.bucketname, args.objectName)}")
        else:
            print("Object name is required to set object access policy.")

    if args.url:
        if args.download_upload_file == "True":
            print(download_file_and_upload_to_s3(s3_client, args.bucketname, args.url, args.keep_local))


# poetry run python task4.py "myBucket" -o "myObject" --set_object_access_policy 
# poetry run python task4.py "myBucket"  --createbucket 
# poetry run python task4.py "myBucket"  --deletebucket 
# poetry run python task4.py "myBucket"  --bucketexists 
# poetry run python task4.py "myBucket"  --create_bucket_policy 
# poetry run python task4.py "myBucket"  --read_bucket_policy 
# poetry run python your_script.py "mybucket" --read_bucket_policy True
# poetry run  python __init__.py "tamar-aws" --download_upload_file -u "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png" -kl True

if __name__ == "__main__":
    main()
