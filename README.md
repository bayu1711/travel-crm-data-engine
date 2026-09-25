# ✈️ Luxury VIP Travel CRM - Data Engine & ETL Pipeline

An end-to-end, production-grade **Data Engineering Solution & ETL Pipeline** built for **Luxury Events and VIP Travel FZCO (Luxury Explorers)**. 

This repository processes 10,000+ raw transactional CRM booking records, handles dirty/inconsistent raw data, cleans and validates business rules, logs quarantined records, uploads data artifacts to **AWS S3**, and ingests production data into an indexed **PostgreSQL** data warehouse.

---

## 🏗️ Architecture & Pipeline Overview

```
 ┌────────────────────────────────┐
 │  Synthetic Raw Data Generator  │  (10,500 records with intentionally dirty formatting,
 └───────────────┬────────────────┘   duplicates, missing fields & invalid ratings)
                 │
                 ▼
 ┌────────────────────────────────┐
 │     AWS S3 Raw Data Lake       │  s3://luxury-travel-crm-data-lake/raw/raw_travel_bookings.csv
 └───────────────┬────────────────┘
                 │
                 ▼
 ┌────────────────────────────────┐
 │   Python ETL Pipeline Engine   │  - Field Casing & Trimming (.title(), .upper())
 │  (src/cleaner.py & validator)  │  - Price Parsing ($12,500.00 USD -> 12500.0)
 └───────┬───────┬────────────────┘  - Safe Date Normalization (ISO YYYY-MM-DD)
         │       │                   - Constraint Check: Rating [1.0 - 5.0], Email format
         ▼       ▼
 ┌──────────────┐  ┌──────────────┐
 │ Valid Records│  │ Quarantined  │
 │ (7,933 rows) │  │ (2,567 rows) │
 └───────┬──────┘  └───────┬──────┘
         │                 │
         ├───► AWS S3 ◄────┤          s3://.../processed/ & s3://.../rejected/
         │
         ▼
 ┌────────────────────────────────┐
 │   PostgreSQL Data Warehouse    │  - Landing Staging: raw_travel_bookings
 │     (sql/schema.sql)           │  - Production Fact: fact_travel_bookings (Indexed)
 └────────────────────────────────┘  - Rejection Audit: etl_rejected_records (JSONB)
```

---

## 📁 Repository Structure

```
travel-crm-data-engine/
│
├── data/                       # Local data directory (.gitignored CSV contents)
│   ├── raw/                    # Raw generated dataset (raw_travel_bookings.csv)
│   ├── cleaned/                # Processed valid dataset (cleaned_travel_bookings.csv)
│   └── rejected/               # Quarantined invalid records (rejected_travel_bookings.csv)
│
├── sql/                        # SQL Schema DDL and Analytical Queries
│   ├── schema.sql              # Database DDL (raw_travel_bookings, fact_travel_bookings, etl_rejected_records)
│   ├── indexes.sql             # B-Tree Indexing Strategy
│   └── queries.sql             # Analytical queries with EXPLAIN ANALYZE performance benchmarks
│
├── src/                        # Modular ETL Pipeline Engine
│   ├── __init__.py
│   ├── config.py               # Environment configuration loader
│   ├── cleaner.py              # Data formatting & normalization transformer
│   ├── validator.py            # Business constraint validation engine
│   ├── s3_service.py           # AWS S3 integration service (Boto3 & LocalStack support)
│   └── db_loader.py            # PostgreSQL database loader via SQLAlchemy & Psycopg2
│
├── scripts/
│   └── generate_dataset.py     # Generator script for >= 10,000 synthetic raw records with data defects
│
├── tests/                      # Unit Test Suite (PyTest)
│   ├── test_cleaner.py         # Tests for field cleaning, casing, price/date parsing
│   └── test_validator.py       # Tests for email regex, price bounds, rating constraints
│
├── .env.example                # Template for environment variables (No hardcoded secrets)
├── docker-compose.yml          # Containerized PostgreSQL & LocalStack S3 environment
├── requirements.txt            # Python dependencies
├── run_pipeline.py             # Main CLI execution entry point
└── README.md                   # Complete technical documentation & architecture guide
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- **Python 3.9+**
- **Docker & Docker Compose** (Optional for local containerized PostgreSQL + S3 mock)

### 2. Quick Setup
Clone the repository and run setup via Makefile:

```bash
git clone https://github.com/bayu1711/travel-crm-data-engine.git
cd travel-crm-data-engine

# Copy environment template
cp .env.example .env

# Install dependencies into virtual environment
make install
```

### 3. Developer Workflow Commands (`Makefile`)
- **`make run`**: Executes the full end-to-end ETL pipeline.
- **`make test`**: Runs the `pytest` unit test suite.
- **`make generate-data`**: Generates a fresh batch of 10,500 synthetic raw records.
- **`make docker-up`**: Spins up PostgreSQL & LocalStack container services.
- **`make clean`**: Purges generated output datasets and Python cache.

### 4. Spin up Docker Services (PostgreSQL & LocalStack S3)
```bash
make docker-up
```

### 5. Run the ETL Pipeline
Execute the main pipeline:

```bash
make run
```

*Note: If Docker/PostgreSQL is not running, the pipeline automatically executes in file-processing mode and outputs cleaned/rejected CSVs locally.*

### 6. Run Unit Tests
Validate pipeline transformation modules using `pytest`:

```bash
make test
```

---

## 📊 Database Design & Indexing Optimization

### Schema Overview (`sql/schema.sql`)
1. **`raw_travel_bookings`**: Staging landing table storing exact raw strings for auditing.
2. **`fact_travel_bookings`**: Production analytics table with enforced primary keys, strict data types (`NUMERIC(12,2)`, `DATE`), and check constraints (`rating BETWEEN 1.0 AND 5.0`, `price >= 0`).
3. **`etl_rejected_records`**: Rejection log storing uncleaned raw payload as `JSONB` alongside specific rejection reasons.

### Indexing Strategy (`sql/indexes.sql`)
High-cardinality and frequent aggregation columns are indexed using B-Tree indexes:
- `idx_fact_travel_category` on `fact_travel_bookings(category)`
- `idx_fact_travel_country` on `fact_travel_bookings(country)`
- `idx_fact_travel_booking_date` on `fact_travel_bookings(booking_date)`
- `idx_fact_travel_country_category` composite index on `(country, category)`

### Analytical Queries (`sql/queries.sql`)
1. **Top Service Categories by Revenue & Volume**
2. **Monthly Revenue & Growth Trend Analysis (`LAG()` Window Function)**
3. **Regional VIP Performance & Customer Satisfaction by Country**

---

## ☁️ AWS S3 Integration

The pipeline leverages **`boto3`** for seamless cloud integration:
- **Raw Data Ingestion**: Uploads raw CSV to `s3://<bucket>/raw/raw_travel_bookings.csv` before processing.
- **Processed Backups**: Uploads clean production data to `s3://<bucket>/processed/` and rejected records to `s3://<bucket>/rejected/`.
- **Local Emulation**: Supports **LocalStack** on `http://localhost:4566` for local testing without AWS charges.
- **Security**: Zero hardcoded secrets; credentials injected via `.env`.

---

## 🚀 Scalability & Architecture Thinking (1M+ Records)

For detailed architectural trade-offs, see [ADR 0001: Architecture & ETL Design Decisions](file:///Users/faza/.gemini/antigravity/scratch/travel-crm-data-engine/docs/adr/0001-etl-architecture-decisions.md).

When scaling from 10,000 to 1,000,000+ daily records, the architecture evolves:

1. **Distributed ETL Processing (Apache PySpark / Dask)**
   - Transition from in-memory Pandas to **PySpark** or **AWS Glue / EMR** to distribute matrix cleaning across clusters.
2. **Orchestration & Workflow Management (Apache Airflow / Prefect)**
   - Replace one-off CLI execution with an **Airflow DAG** featuring backfilling, SLA tracking, retries, and Slack alert webhooks.
3. **Database Partitioning Strategy**
   - Implement **PostgreSQL Table Partitioning** by `RANGE (booking_date)` (monthly or annual partitions) to maintain query speed on multi-million row tables.
4. **Data Warehousing Transition**
   - Shift production reporting from PostgreSQL to columnar cloud data warehouses (**Snowflake** or **AWS Redshift** / **Databricks Delta Lake**).

