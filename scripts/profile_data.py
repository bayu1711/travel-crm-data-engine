"""
Data Profiling Script
Inspects raw CSV statistics, null counts, min/max bounds, and string anomalies.
"""

import pandas as pd

def profile_raw_data(file_path: str = "data/raw/raw_travel_bookings.csv"):
    df = pd.read_csv(file_path)
    print("=" * 50)
    print("RAW DATASET PROFILING REPORT")
    print("=" * 50)
    print(f"Total Rows: {len(df)}")
    
    print("\n1. MISSING VALUES PER COLUMN:")
    print(df.isnull().sum())
    
    print("\n2. RATING MIN/MAX BOUND CHECK:")
    ratings = pd.to_numeric(df["rating"], errors="coerce")
    print(f"   Min Rating Found: {ratings.min()}")
    print(f"   Max Rating Found: {ratings.max()}  (Allowed: 1.0 - 5.0)")
    
    print("\n3. NON-NUMERIC PRICE FORMAT SAMPLES:")
    non_numeric = df[pd.to_numeric(df["price"], errors="coerce").isna()]["price"].unique()[:5]
    print(f"   Sample Dirty Prices: {non_numeric}")

    print("\n4. PAYMENT STATUS VALUES FOUND:")
    print(f"   Statuses: {df['payment_status'].dropna().unique()}")

if __name__ == "__main__":
    profile_raw_data()
