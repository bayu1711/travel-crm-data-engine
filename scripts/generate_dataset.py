import os
import random
import argparse
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

CATEGORIES = [
    "Private Jet", "Superyacht", "Luxury Villa", "5-Star Hotel",
    "VIP Dining", "Chauffeur Service", "Helicopter Transfer", "Private Island"
]

COUNTRIES = [
    "United Arab Emirates", "United States", "United Kingdom", "France",
    "Switzerland", "Monaco", "Italy", "Japan", "Maldives", "Singapore"
]

PAYMENT_STATUSES = ["COMPLETED", "PENDING", "REFUNDED", "FAILED"]

def generate_dirty_date(base_date):
    rand = random.random()
    if rand < 0.03:
        return None
    elif rand < 0.06:
        return "INVALID_DATE_FORMAT"
    elif rand < 0.30:
        return base_date.strftime("%Y/%m/%d")
    elif rand < 0.50:
        return base_date.strftime("%d-%b-%Y")
    elif rand < 0.70:
        return base_date.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return base_date.strftime("%Y-%m-%d")

def generate_dirty_price():
    rand = random.random()
    base_price = round(random.uniform(500, 50000), 2)
    if rand < 0.03:
        return None
    elif rand < 0.06:
        return -round(random.uniform(100, 2000), 2)
    elif rand < 0.20:
        return f"${base_price:,.2f}"
    elif rand < 0.30:
        return f"{base_price} USD"
    else:
        return base_price

def generate_dirty_rating():
    rand = random.random()
    if rand < 0.04:
        return None
    elif rand < 0.07:
        return round(random.uniform(5.1, 9.9), 1)
    elif rand < 0.09:
        return round(random.uniform(-3.0, 0.0), 1)
    else:
        return round(random.uniform(3.0, 5.0), 1)

def generate_dirty_casing(text):
    if not text:
        return text
    rand = random.random()
    if rand < 0.25:
        return text.lower()
    elif rand < 0.40:
        return text.upper()
    return text

def generate_raw_dataset(num_records=10500, output_path="data/raw/raw_travel_bookings.csv"):
    print(f"Generating {num_records} raw records for Luxury VIP Travel CRM...")
    
    records = []
    base_start_date = datetime(2023, 1, 1)

    for i in range(1, num_records + 1):
        booking_id = f"BK-{10000 + i}"
        
        # Inject intentional duplicate booking IDs (~2% rate)
        if random.random() < 0.02 and i > 50:
            booking_id = f"BK-{10000 + (i - random.randint(1, 30))}"
        
        name = fake.name()
        if random.random() < 0.03:
            name = None
        else:
            name = generate_dirty_casing(name)
            
        email = fake.email()
        if random.random() < 0.04:
            email = "bad_email_without_at_domain"
        elif random.random() < 0.02:
            email = None
            
        category = generate_dirty_casing(random.choice(CATEGORIES))
        country = random.choice(COUNTRIES)
        price = generate_dirty_price()
        rating = generate_dirty_rating()
        payment_status = generate_dirty_casing(random.choice(PAYMENT_STATUSES))
        
        random_days = random.randint(0, 600)
        created_date = generate_dirty_date(base_start_date + timedelta(days=random_days))
        
        records.append({
            "booking_id": booking_id,
            "customer_name": name,
            "customer_email": email,
            "category": category,
            "price": price,
            "rating": rating,
            "country": country,
            "payment_status": payment_status,
            "created_date": created_date
        })

    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    # quick sanity print so you can see what the dirty data looks like without opening a CSV
    n_null_price = df['price'].isnull().sum()
    n_null_name = df['customer_name'].isnull().sum()
    n_dupe_ids = df.duplicated('booking_id').sum()
    print(f"Generated {len(df)} records -> {output_path}")
    print(f"  Nulls: customer_name={n_null_name}, price={n_null_price} | Duplicate booking_ids: {n_dupe_ids}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthetic Raw Dataset Generator for VIP Travel CRM")
    parser.add_argument("--count", type=int, default=10500, help="Number of records to generate (default: 10500)")
    parser.add_argument("--output", type=str, default="data/raw/raw_travel_bookings.csv", help="Output CSV path")
    args = parser.parse_args()

    generate_raw_dataset(num_records=args.count, output_path=args.output)
