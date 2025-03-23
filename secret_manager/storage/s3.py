"""S3 storage backend for Secret Manager."""

from pathlib import Path

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from secret_manager.storage.base import StorageBackend
from secret_manager.utils import logger


class S3StorageBackend(StorageBackend):
    """AWS S3 storage backend."""

    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, region: str):
        self.client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region,
            config = Config(
                signature_version="s3v4", s3={"use_accelerate_endpoint": False}
            ),
        )


    def write(self, key: str, local_path: Path):
        """Write data to S3"""

        try:
            bucket, s3_key = key.split("/", 1)
            self.client.upload_file(
                Filename=local_path.as_posix(),
                Bucket=bucket,
                Key=s3_key,
            )

            logger.info(f"Pushed changes to s3://{bucket}/{s3_key}")
            return 0
        
        except Exception as e:
            logger.error(f"Failed to write to s3://{bucket}/{s3_key} :: {e}")
            return 1


    def read(self, key: str):
        """Read data from S3"""

        bucket, s3_key = key.split("/", 1)
        response = self.client.get_object(Bucket=bucket, Key=s3_key)

        data = response["Body"].readlines()
        decoded_lines = [line.decode().strip() for line in data]
        lines = [line for line in decoded_lines if line]

        return lines
    

    def exists(self, key: str):
        try:
            bucket, s3_key = key.split("/", 1)
            self.client.head_object(Bucket=bucket, Key=s3_key)
            return True
        except ClientError:
            return False


