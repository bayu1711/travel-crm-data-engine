import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Settings
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "travel_crm_db")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres_secure_pass")

    @classmethod
    def get_db_url(cls) -> str:
        return f"postgresql://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"

    # AWS & S3 Settings
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME", "luxury-travel-crm-data-lake")
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL", "")

    # Storage Paths
    RAW_DATA_PATH = os.getenv("RAW_DATA_PATH", "data/raw/raw_travel_bookings.csv")
    CLEAN_DATA_PATH = os.getenv("CLEAN_DATA_PATH", "data/cleaned/cleaned_travel_bookings.csv")
    REJECTED_DATA_PATH = os.getenv("REJECTED_DATA_PATH", "data/rejected/rejected_travel_bookings.csv")
