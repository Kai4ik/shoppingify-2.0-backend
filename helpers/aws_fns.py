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


def upload_file(username, receipt_number, file):
    try:
        s3_client.put_object(Body=file.file, Bucket="shoppingify-receipts", Key=f'{username}/{receipt_number}.jpg')
    except ClientError as e:
        logging.error(e)
        return False
    return True


def save_receipt_to_s3(username: str, receipt_number: int, file):
    create_bucket()
    upload_file(username, receipt_number, file)
