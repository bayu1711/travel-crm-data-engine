"""
Unit Tests for DataValidator Module
"""

import pandas as pd
from src.validator import DataValidator

def test_validator_valid_record():
    row = pd.Series({
        "booking_id": "BK-200",
        "customer_name": "Alice Smith",
        "customer_email": "alice@example.com",
        "category": "Superyacht",
        "price": 25000.0,
        "rating": 4.9,
        "country": "Monaco",
        "payment_status": "COMPLETED",
        "booking_date": "2024-06-01"
    })
    is_valid, reason = DataValidator.validate_record(row, set())
    assert is_valid is True
    assert reason == "VALID"

def test_validator_missing_required_field():
    row = pd.Series({
        "booking_id": "BK-201",
        "customer_name": None,
        "customer_email": "alice@example.com",
        "category": "Superyacht",
        "price": 25000.0,
        "rating": 4.9,
        "country": "Monaco",
        "payment_status": "COMPLETED",
        "booking_date": "2024-06-01"
    })
    is_valid, reason = DataValidator.validate_record(row, set())
    assert is_valid is False
    assert "Missing required fields" in reason

def test_validator_duplicate_id():
    row = pd.Series({
        "booking_id": "BK-200",
        "customer_name": "Alice Smith",
        "customer_email": "alice@example.com",
        "category": "Superyacht",
        "price": 25000.0,
        "rating": 4.9,
        "country": "Monaco",
        "payment_status": "COMPLETED",
        "booking_date": "2024-06-01"
    })
    seen = {"BK-200"}
    is_valid, reason = DataValidator.validate_record(row, seen)
    assert is_valid is False
    assert "Duplicate booking_id" in reason

def test_validator_invalid_email():
    row = pd.Series({
        "booking_id": "BK-202",
        "customer_name": "Bob Jones",
        "customer_email": "invalid_email_no_at",
        "category": "Luxury Villa",
        "price": 5000.0,
        "rating": 4.0,
        "country": "Switzerland",
        "payment_status": "COMPLETED",
        "booking_date": "2024-06-01"
    })
    is_valid, reason = DataValidator.validate_record(row, set())
    assert is_valid is False
    assert "Invalid email format" in reason

def test_validator_out_of_bounds_rating():
    row = pd.Series({
        "booking_id": "BK-203",
        "customer_name": "Charlie Brown",
        "customer_email": "charlie@example.com",
        "category": "5-Star Hotel",
        "price": 1200.0,
        "rating": 8.5,  # Out of bounds
        "country": "Japan",
        "payment_status": "COMPLETED",
        "booking_date": "2024-06-01"
    })
    is_valid, reason = DataValidator.validate_record(row, set())
    assert is_valid is False
    assert "Rating out of bounds" in reason


def test_validator_null_rating_is_allowed():
    # rating is optional — not every customer leaves a review
    row = pd.Series({
        "booking_id": "BK-204",
        "customer_name": "Diana Prince",
        "customer_email": "diana@luxe.com",
        "category": "Private Island",
        "price": 45000.0,
        "rating": None,
        "country": "Maldives",
        "payment_status": "COMPLETED",
        "booking_date": "2024-03-15"
    })
    is_valid, reason = DataValidator.validate_record(row, set())
    assert is_valid is True


def test_validator_unknown_payment_status():
    # found in dataset: casing not normalised upstream produces garbage like "cOMPLETED"
    row = pd.Series({
        "booking_id": "BK-205",
        "customer_name": "Eve Torres",
        "customer_email": "eve@example.com",
        "category": "Superyacht",
        "price": 15000.0,
        "rating": 4.2,
        "country": "Monaco",
        "payment_status": "cOMPLETED",   # would be rejected if cleaner didn't catch it
        "booking_date": "2024-04-01"
    })
    is_valid, reason = DataValidator.validate_record(row, set())
    assert is_valid is False
    assert "Unknown payment_status" in reason


def test_validator_bad_email_from_dataset():
    # the generator injects exactly this string as a malformed email
    row = pd.Series({
        "booking_id": "BK-206",
        "customer_name": "Frank Castle",
        "customer_email": "bad_email_without_at_domain",
        "category": "Luxury Villa",
        "price": 8000.0,
        "rating": 3.5,
        "country": "France",
        "payment_status": "COMPLETED",
        "booking_date": "2024-02-20"
    })
    is_valid, reason = DataValidator.validate_record(row, set())
    assert is_valid is False
    assert "Invalid email format" in reason

