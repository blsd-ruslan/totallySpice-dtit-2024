from dotenv import load_dotenv
import os

load_dotenv()

# API
OPEN_API_KEY = os.getenv("OPEN_API_KEY")

# DATABASE
DATABASE_URL = os.getenv("DATABASE_URL")

# MINIO
MINIO_URL = os.getenv("MINIO_URL")
MINIO_USER = os.getenv("MINIO_USER")
MINIO_PASSWORD = os.getenv("MINIO_PASSWORD")

