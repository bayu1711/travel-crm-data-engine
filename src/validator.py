import re
import pandas as pd
from loguru import logger
from typing import Tuple

class DataValidator:
    EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

    @classmethod
    def validate_record(cls, row: pd.Series, seen_booking_ids: set) -> Tuple[bool, str]:
        booking_id = row.get("booking_id")
        
        required_fields = ["booking_id", "customer_name", "customer_email", "category", "price", "country", "payment_status", "booking_date"]
        missing_fields = [f for f in required_fields if pd.isna(row.get(f)) or row.get(f) is None]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"

        if booking_id in seen_booking_ids:
            return False, f"Duplicate booking_id: '{booking_id}'"
        
        email = str(row.get("customer_email", ""))
        if not cls.EMAIL_REGEX.match(email):
            return False, f"Invalid email format: '{email}'"

        price = row.get("price")
        if price is None or price < 0:
            return False, f"Invalid price value: {price} (must be >= 0)"

        # only allow known statuses into the fact table — reject anything else (typos, malformed)
        VALID_STATUSES = {"COMPLETED", "PENDING", "REFUNDED", "FAILED"}
        status = row.get("payment_status", "")
        if status not in VALID_STATUSES:
            return False, f"Unknown payment_status: '{status}'"

        rating = row.get("rating")
        if pd.notna(rating) and rating is not None:
            if rating < 1.0 or rating > 5.0:
                return False, f"Rating out of bounds: {rating} (allowed: 1.0-5.0)"

        return True, "VALID"

    @classmethod
    def validate_dataframe(cls, cleaned_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        logger.info(f"Validating {len(cleaned_df)} records against business rules...")
        
        valid_rows = []
        rejected_rows = []
        seen_booking_ids = set()

        for _, row in cleaned_df.iterrows():
            is_valid, reason = cls.validate_record(row, seen_booking_ids)
            
            if is_valid:
                seen_booking_ids.add(row["booking_id"])
                valid_rows.append(row.to_dict())
            else:
                row_dict = row.to_dict()
                row_dict["rejection_reason"] = reason
                rejected_rows.append(row_dict)

        valid_df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame()
        rejected_df = pd.DataFrame(rejected_rows) if rejected_rows else pd.DataFrame()

        logger.info(f"Validation complete: {len(valid_df)} valid, {len(rejected_df)} quarantined.")
        return valid_df, rejected_df
