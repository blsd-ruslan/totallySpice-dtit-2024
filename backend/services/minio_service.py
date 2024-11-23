from minio import Minio
from minio.error import S3Error
import io
import os

from utils.environment_variables import MINIO_URL, MINIO_USER, MINIO_PASSWORD

# Configure MinIO client
MINIO_CLIENT = Minio(
    MINIO_URL,  # Replace with your MinIO server address
    access_key=MINIO_USER,  # Replace with your access key
    secret_key=MINIO_PASSWORD,  # Replace with your secret key
    secure=False
)

BUCKET_NAME = "user"

# Ensure the bucket exists
found = MINIO_CLIENT.bucket_exists(BUCKET_NAME)
if not found:
    MINIO_CLIENT.make_bucket(BUCKET_NAME)

async def upload_file_to_minio(file):
    try:
        file_data = await file.read()
        MINIO_CLIENT.put_object(
            BUCKET_NAME,
            file.filename,
            data=io.BytesIO(file_data),
            length=len(file_data),
            content_type='application/pdf'
        )
    except S3Error as err:
        raise Exception(f"Failed to upload {file.filename}: {str(err)}")
