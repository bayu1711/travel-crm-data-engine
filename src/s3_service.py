"""
AWS S3 Service Module
Handles uploading raw datasets, cleaned output datasets, and backups to S3.
Supports both AWS S3 Free Tier and local LocalStack emulation seamlessly.
"""

import os
import boto3
from botocore.exceptions import ClientError
from loguru import logger
from src.config import Config

class S3Service:
    def __init__(self):
        self.bucket_name = Config.AWS_S3_BUCKET_NAME
        
        # Initialize boto3 client with optional endpoint_url for LocalStack
        kwargs = {
            "service_name": "s3",
            "region_name": Config.AWS_REGION,
            "aws_access_key_id": Config.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": Config.AWS_SECRET_ACCESS_KEY,
        }
        
        if Config.AWS_S3_ENDPOINT_URL and Config.AWS_S3_ENDPOINT_URL.strip():
            kwargs["endpoint_url"] = Config.AWS_S3_ENDPOINT_URL.strip()
            
        self.s3_client = boto3.client(**kwargs)

    def create_bucket_if_not_exists(self):
        """Creates the target S3 bucket if it does not already exist."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"S3 Bucket '{self.bucket_name}' exists.")
        except ClientError:
            try:
                logger.info(f"Creating S3 Bucket '{self.bucket_name}'...")
                if Config.AWS_REGION == "us-east-1":
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                else:
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={"LocationConstraint": Config.AWS_REGION}
                    )
                logger.success(f"S3 Bucket '{self.bucket_name}' created successfully.")
            except Exception as e:
                logger.warning(f"Could not create bucket '{self.bucket_name}': {e}")

    def upload_file(self, local_file_path: str, s3_key: str) -> bool:
        """Uploads a local file to the configured S3 bucket."""
        if not os.path.exists(local_file_path):
            logger.error(f"Local file '{local_file_path}' not found for S3 upload.")
            return False

        try:
            self.create_bucket_if_not_exists()
            logger.info(f"Uploading '{local_file_path}' to s3://{self.bucket_name}/{s3_key}...")
            self.s3_client.upload_file(local_file_path, self.bucket_name, s3_key)
            logger.success(f"Successfully uploaded to s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            logger.warning(f"Failed to upload '{local_file_path}' to S3: {e}")
            return False

    def download_file(self, s3_key: str, local_file_path: str) -> bool:
        """Downloads a file from S3 to local filesystem."""
        try:
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            logger.info(f"Downloading s3://{self.bucket_name}/{s3_key} to '{local_file_path}'...")
            self.s3_client.download_file(self.bucket_name, s3_key, local_file_path)
            logger.success(f"Successfully downloaded s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            logger.warning(f"Failed to download '{s3_key}' from S3: {e}")
            return False
