import boto3
from botocore.exceptions import ClientError
import os
import logging

s3_client = boto3.client("s3", region_name='us-east-1', aws_access_key_id=os.getenv("aws_access_key_id"), aws_secret_access_key=os.getenv("aws_secret_access_key"))


def create_bucket():
    try:
        s3_client.create_bucket(Bucket="shoppingify-receipts")
    except ClientError as e:
        logging.error(e)
        return False
    return True


def upload_file():
    try:
        s3_client.create_bucket(Bucket="shoppingify-receipts")
    except ClientError as e:
        logging.error(e)
        return False
    return True


def save_receipt_to_s3():
    create_bucket()
