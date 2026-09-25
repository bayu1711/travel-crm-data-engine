-- Database schema for VIP Travel CRM data pipeline
-- Tables: raw staging, cleaned fact, and rejection audit log

-- drop order matters if you add FKs later; CASCADE handles views/deps
DROP TABLE IF EXISTS fact_travel_bookings CASCADE;
DROP TABLE IF EXISTS etl_rejected_records CASCADE;
DROP TABLE IF EXISTS raw_travel_bookings CASCADE;

-- landing zone: raw strings exactly as they arrive from CSV
CREATE TABLE raw_travel_bookings (
    raw_id SERIAL PRIMARY KEY,
    booking_id VARCHAR(100),
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    category VARCHAR(100),
    price VARCHAR(100),         -- stored as string; may contain "$12,500.00 USD" etc.
    rating VARCHAR(50),         -- stored as string; may be out of range
    country VARCHAR(100),
    payment_status VARCHAR(50),
    created_date VARCHAR(100),  -- stored as string; mixed formats handled in ETL
    ingested_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- production fact table: typed, constrained, indexed
CREATE TABLE fact_travel_bookings (
    booking_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(150) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price NUMERIC(12, 2) NOT NULL CHECK (price >= 0),
    rating NUMERIC(2, 1) CHECK (rating >= 1.0 AND rating <= 5.0),  -- NUMERIC(2,1) = max 9.9
    country VARCHAR(100) NOT NULL,
    payment_status VARCHAR(50) NOT NULL,
    booking_date DATE NOT NULL,
    processed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- quarantine log: keeps raw JSONB payload alongside the reason it was rejected
CREATE TABLE etl_rejected_records (
    rejection_id SERIAL PRIMARY KEY,
    booking_id VARCHAR(100),
    rejection_reason TEXT NOT NULL,
    raw_record JSONB NOT NULL,
    rejected_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
