"""
Database Loader Module
Interacts with PostgreSQL database using SQLAlchemy.
Executes schema DDL, loads valid records into fact table, and quarantines rejected records into audit log.
"""

import json
import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
from src.config import Config

class DatabaseLoader:
    def __init__(self):
        self.db_url = Config.get_db_url()
        self.engine = create_engine(self.db_url, echo=False)

    def test_connection(self) -> bool:
        """Tests database connectivity."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1;"))
            logger.info("Database connection test successful.")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

    def init_schema(self, schema_sql_path: str = "sql/schema.sql"):
        """Initializes database schema tables from DDL file."""
        logger.info(f"Initializing database schema from '{schema_sql_path}'...")
        try:
            with open(schema_sql_path, "r") as f:
                sql_script = f.read()
            
            with self.engine.connect() as conn:
                conn.execute(text(sql_script))
                conn.commit()
            logger.success("Database schema initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize schema DDL: {e}")
            raise

    def load_raw_data(self, raw_df: pd.DataFrame):
        """Loads raw dataset into staging table raw_travel_bookings."""
        if raw_df.empty:
            return
        
        logger.info(f"Loading {len(raw_df)} raw records into 'raw_travel_bookings' staging table...")
        staging_df = raw_df.copy()
        staging_df.to_sql(
            "raw_travel_bookings",
            con=self.engine,
            if_exists="append",
            index=False
        )
        logger.success("Raw staging data successfully loaded.")

    def load_fact_data(self, valid_df: pd.DataFrame):
        """Loads cleaned valid records into target fact table fact_travel_bookings."""
        if valid_df.empty:
            logger.warning("No valid records to load into fact_travel_bookings.")
            return

        logger.info(f"Loading {len(valid_df)} valid records into 'fact_travel_bookings'...")
        
        # Select target columns matching DDL schema
        fact_cols = ["booking_id", "customer_name", "customer_email", "category", "price", "rating", "country", "payment_status", "booking_date"]
        target_df = valid_df[fact_cols].copy()

        target_df.to_sql(
            "fact_travel_bookings",
            con=self.engine,
            if_exists="append",
            index=False
        )
        logger.success("Fact data successfully loaded into PostgreSQL.")

    def load_rejected_data(self, rejected_df: pd.DataFrame):
        """Loads rejected records into etl_rejected_records quarantine table."""
        if rejected_df.empty:
            logger.info("Zero rejected records encountered.")
            return

        logger.info(f"Loading {len(rejected_df)} rejected records into 'etl_rejected_records' audit table...")
        
        audit_records = []
        for _, row in rejected_df.iterrows():
            booking_id = row.get("booking_id")
            reason = row.get("rejection_reason", "Validation failed")
            
            # Convert row to clean JSON payload
            raw_dict = row.to_dict()
            raw_dict.pop("rejection_reason", None)
            
            audit_records.append({
                "booking_id": str(booking_id) if pd.notna(booking_id) else None,
                "rejection_reason": reason,
                "raw_record": json.dumps(raw_dict, default=str)
            })

        audit_df = pd.DataFrame(audit_records)
        audit_df.to_sql(
            "etl_rejected_records",
            con=self.engine,
            if_exists="append",
            index=False
        )
        logger.success("Rejected records audit log loaded.")

    def apply_indexes(self, index_sql_path: str = "sql/indexes.sql"):
        """Applies database performance indexing strategy."""
        logger.info(f"Applying database indexes from '{index_sql_path}'...")
        try:
            with open(index_sql_path, "r") as f:
                sql_script = f.read()
            
            with self.engine.connect() as conn:
                conn.execute(text(sql_script))
                conn.commit()
            logger.success("Database indexes created successfully.")
        except Exception as e:
            logger.warning(f"Could not apply indexes: {e}")
