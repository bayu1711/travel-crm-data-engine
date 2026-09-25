import os
import argparse
import pandas as pd
from loguru import logger

from src.config import Config
from src.s3_service import S3Service
from src.cleaner import DataCleaner
from src.validator import DataValidator
from src.db_loader import DatabaseLoader

def run_pipeline(skip_s3=False, skip_db=False):
    logger.info("--- Luxury VIP Travel CRM: ETL pipeline starting ---")

    raw_path = Config.RAW_DATA_PATH
    clean_path = Config.CLEAN_DATA_PATH
    rejected_path = Config.REJECTED_DATA_PATH

    # Step 1: Extract
    if not os.path.exists(raw_path):
        logger.info(f"Raw dataset not found at '{raw_path}', generating synthetic data...")
        from scripts.generate_dataset import generate_raw_dataset
        generate_raw_dataset(num_records=10500, output_path=raw_path)

    raw_df = pd.read_csv(raw_path)
    logger.info(f"Loaded {len(raw_df)} raw records from '{raw_path}'.")

    # Step 2: Upload raw to S3
    if not skip_s3:
        s3_service = S3Service()
        s3_service.upload_file(raw_path, "raw/raw_travel_bookings.csv")
    else:
        logger.info("Skipping S3 upload (--skip-s3 flag set).")

    # Step 3: Clean
    cleaned_df = DataCleaner.process_dataframe(raw_df)

    # Step 4: Validate
    valid_df, rejected_df = DataValidator.validate_dataframe(cleaned_df)

    os.makedirs(os.path.dirname(clean_path), exist_ok=True)
    os.makedirs(os.path.dirname(rejected_path), exist_ok=True)
    valid_df.to_csv(clean_path, index=False)
    rejected_df.to_csv(rejected_path, index=False)

    logger.success(f"Cleaned: {len(valid_df)} records → '{clean_path}'")
    logger.info(f"Rejected: {len(rejected_df)} records → '{rejected_path}'")

    # Step 5: Upload processed files to S3
    if not skip_s3:
        s3_service.upload_file(clean_path, "processed/cleaned_travel_bookings.csv")
        s3_service.upload_file(rejected_path, "rejected/rejected_travel_bookings.csv")

    # Step 6: Load into PostgreSQL
    if not skip_db:
        db_loader = DatabaseLoader()
        if db_loader.test_connection():
            db_loader.init_schema("sql/schema.sql")
            db_loader.load_raw_data(raw_df)
            db_loader.load_fact_data(valid_df)
            db_loader.load_rejected_data(rejected_df)
            db_loader.apply_indexes("sql/indexes.sql")
            logger.success("Database ingestion complete.")
        else:
            logger.warning("Could not reach PostgreSQL — skipping DB load.")
    else:
        logger.info("Skipping database load (--skip-db flag set).")

    logger.info(f"Done. Raw={len(raw_df)} | Valid={len(valid_df)} | Rejected={len(rejected_df)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the VIP Travel CRM ETL pipeline")
    parser.add_argument("--skip-s3", action="store_true", help="Skip all S3 uploads")
    parser.add_argument("--skip-db", action="store_true", help="Skip PostgreSQL ingestion")
    args = parser.parse_args()

    run_pipeline(skip_s3=args.skip_s3, skip_db=args.skip_db)
