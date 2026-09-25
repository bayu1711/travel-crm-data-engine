"""
Unit Tests for DataCleaner Module
"""

import pandas as pd
from src.cleaner import DataCleaner


def test_clean_price():
    assert DataCleaner.clean_price("$12,500.00") == 12500.0
    assert DataCleaner.clean_price("500.5 USD") == 500.5
    assert DataCleaner.clean_price(1500) == 1500.0
    assert DataCleaner.clean_price(None) is None
    assert DataCleaner.clean_price("-250") == -250.0


def test_clean_rating():
    assert DataCleaner.clean_rating("4.8") == 4.8
    assert DataCleaner.clean_rating(5.0) == 5.0
    assert DataCleaner.clean_rating(None) is None
    assert DataCleaner.clean_rating("invalid") is None


def test_clean_date():
    assert DataCleaner.clean_date("2024-05-12") == "2024-05-12"
    assert DataCleaner.clean_date("2024/05/12") == "2024-05-12"
    assert DataCleaner.clean_date("12-May-2024") == "2024-05-12"
    assert DataCleaner.clean_date("INVALID_DATE") is None
    assert DataCleaner.clean_date(None) is None


def test_process_dataframe():
    data = {
        "booking_id": ["BK-101"],
        "customer_name": ["john doe"],
        "customer_email": ["JOHN@EXAMPLE.COM"],
        "category": ["private jet"],
        "price": ["$15,000.00"],
        "rating": ["4.9"],
        "country": ["united arab emirates"],
        "payment_status": ["completed"],
        "created_date": ["2024/01/15"]
    }
    df = pd.DataFrame(data)
    cleaned = DataCleaner.process_dataframe(df)

    assert cleaned["customer_name"].iloc[0] == "John Doe"
    assert cleaned["customer_email"].iloc[0] == "john@example.com"
    assert cleaned["category"].iloc[0] == "Private Jet"
    assert cleaned["price"].iloc[0] == 15000.0
    assert cleaned["rating"].iloc[0] == 4.9
    assert cleaned["country"].iloc[0] == "United Arab Emirates"
    assert cleaned["payment_status"].iloc[0] == "COMPLETED"
    assert cleaned["booking_date"].iloc[0] == "2024-01-15"


# --- edge cases found while running the real dataset ---

def test_clean_price_zero_is_valid():
    # a free transfer/comp booking should not be treated as missing
    assert DataCleaner.clean_price(0) == 0.0
    assert DataCleaner.clean_price("0.00") == 0.0


def test_clean_date_timestamp_format():
    # generator injects "YYYY-MM-DD HH:MM:SS" strings; make sure we strip the time
    assert DataCleaner.clean_date("2023-06-15 00:00:00") == "2023-06-15"


def test_customer_name_nan_string():
    # pandas read_csv turns some missing values into the string "nan" not Python None
    data = {
        "booking_id": ["BK-999"],
        "customer_name": ["nan"],
        "customer_email": ["test@example.com"],
        "category": ["luxury villa"],
        "price": ["5000"],
        "rating": ["4.0"],
        "country": ["japan"],
        "payment_status": ["completed"],
        "created_date": ["2024-01-01"]
    }
    df = pd.DataFrame(data)
    cleaned = DataCleaner.process_dataframe(df)
    # "nan" should be normalized to None, not kept as the title-cased string "Nan"
    assert cleaned["customer_name"].iloc[0] is None
