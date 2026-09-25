import re
import pandas as pd
from loguru import logger

class DataCleaner:
    """Utility functions for standardizing raw string fields, prices, ratings, and dates."""

    @staticmethod
    def clean_price(val):
        if pd.isna(val) or val is None:
            return None
        if isinstance(val, (int, float)):
            return float(val)
        
        # Strip currency symbols, commas, and trailing currency codes (e.g. "$12,500.00 USD")
        cleaned_str = re.sub(r"[^\d.-]", "", str(val))
        try:
            return float(cleaned_str) if cleaned_str else None
        except ValueError:
            return None

    @staticmethod
    def clean_rating(val):
        if pd.isna(val) or val is None:
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def clean_date(val):
        if pd.isna(val) or val is None or str(val).strip() == "":
            return None
        
        val_str = str(val).strip()
        try:
            # coerce handles dirty string formats like '12-May-2024' or '2024/01/15'
            parsed_dt = pd.to_datetime(val_str, errors="coerce")
            if pd.isna(parsed_dt):
                return None
            return parsed_dt.strftime("%Y-%m-%d")
        except Exception:
            return None

    @classmethod
    def process_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"Normalizing and standardizing {len(df)} raw records...")
        
        cleaned_df = df.copy()
        
        # Trim leading/trailing whitespace across object columns
        for col in cleaned_df.select_dtypes(include="object").columns:
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()

        # Normalize string casing
        cleaned_df["customer_name"] = cleaned_df["customer_name"].apply(
            lambda x: x.title() if x and x.lower() not in ("none", "nan") else None
        )
        cleaned_df["customer_email"] = cleaned_df["customer_email"].apply(
            lambda x: x.lower() if x and x.lower() not in ("none", "nan") else None
        )
        cleaned_df["category"] = cleaned_df["category"].apply(
            lambda x: x.title() if x and x.lower() not in ("none", "nan") else None
        )
        cleaned_df["country"] = cleaned_df["country"].apply(
            lambda x: x.title() if x and x.lower() not in ("none", "nan") else None
        )
        cleaned_df["payment_status"] = cleaned_df["payment_status"].apply(
            lambda x: x.upper() if x and x.lower() not in ("none", "nan") else None
        )

        # Parse numeric and date fields
        cleaned_df["price"] = cleaned_df["price"].apply(cls.clean_price)
        cleaned_df["rating"] = cleaned_df["rating"].apply(cls.clean_rating)
        cleaned_df["booking_date"] = cleaned_df["created_date"].apply(cls.clean_date)

        logger.info("Field standardization finished.")
        return cleaned_df
