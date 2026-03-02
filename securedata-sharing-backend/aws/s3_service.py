# s3_service.py
import boto3
import os

class S3Service:
    def __init__(self, bucket_name, region="ap-south-1"):
        self.bucket_name = bucket_name
        self.s3 = boto3.client("s3", region_name=region)

    def upload_file(self, local_file_path, s3_key):
        """
        Upload encrypted file to S3
        """
        self.s3.upload_file(local_file_path, self.bucket_name, s3_key)
        print(f"[S3] Uploaded {local_file_path} to s3://{self.bucket_name}/{s3_key}")

    def download_file(self, s3_key, download_path):
        """
        Download encrypted file from S3
        """
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        self.s3.download_file(self.bucket_name, s3_key, download_path)
        print(f"[S3] Downloaded s3://{self.bucket_name}/{s3_key}")

    def upload_bytes(self, data: bytes, s3_key: str):
        self.s3.put_object(Bucket=self.bucket_name, Key=s3_key, Body=data)
        print(f"[S3] Uploaded bytes to s3://{self.bucket_name}/{s3_key}")