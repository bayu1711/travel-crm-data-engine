# ADR 0001: Architecture & ETL Design Decisions

- **Status**: Accepted
- **Date**: 2026-09-25
- **Author**: Fazarath

## Context & Problem Statement
Luxury Events and VIP Travel FZCO requires an end-to-end data pipeline to ingest, clean, validate, and store raw VIP travel booking records (10,000+ rows) into an indexed relational data warehouse while maintaining an audit trail for rejected records.

## Decision Drivers
- Data reliability & constraint validation (zero bad data in production tables).
- Rejection tracking & auditability.
- Database query performance optimization.
- AWS cloud integration readiness (S3 / LocalStack).

## Considered Options

### 1. Processing Engine: Pandas vs. PySpark
- **Chosen Option**: **Pandas** for the 10,000–100,000 record scale.
- **Rationale**: Pandas offers low overhead, rapid in-memory processing, and straightforward regex standardizations for datasets under 1 GB. For 1M+ scaling, PySpark on AWS Glue is detailed in the README scaling path.

### 2. Rejection Management: Drop vs. Quarantine Log
- **Chosen Option**: **Quarantine Audit Pattern (`etl_rejected_records` + JSONB)**.
- **Rationale**: Silently dropping corrupt records hides data loss. Halting the pipeline on corrupt rows blocks valid transactions. Quarantining bad records into `etl_rejected_records` with raw JSON payload and rejection reason allows downstream analysis and remediation.

### 3. Database Schema: Flat Fact Table vs. Normalized Star Schema
- **Chosen Option**: **Indexed Fact Table (`fact_travel_bookings`) with landing staging (`raw_travel_bookings`)**.
- **Rationale**: Strikes an optimal balance between simplified ETL ingestion and analytical query speed for financial reporting.

### 4. Indexing Strategy: Targeted B-Tree Indexes
- **Chosen Option**: **B-Tree indexes on `category`, `country`, `booking_date`, and `(country, category)`**.
- **Rationale**: Analytical queries heavily filter and group by regional metrics, time periods, and service categories. B-Tree indexes convert Sequential Scans to Index Scans for these high-cardinality columns.
