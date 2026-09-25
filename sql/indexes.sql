-- B-Tree indexes for the columns used in GROUP BY / ORDER BY / WHERE across analytical queries

CREATE INDEX IF NOT EXISTS idx_fact_travel_category     ON fact_travel_bookings (category);
CREATE INDEX IF NOT EXISTS idx_fact_travel_country      ON fact_travel_bookings (country);
CREATE INDEX IF NOT EXISTS idx_fact_travel_booking_date ON fact_travel_bookings (booking_date);
-- composite for queries that filter by both country and category
CREATE INDEX IF NOT EXISTS idx_fact_travel_country_category ON fact_travel_bookings (country, category);
