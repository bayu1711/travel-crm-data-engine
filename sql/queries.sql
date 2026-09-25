-- Analytical queries for VIP travel booking insights

-- Revenue and booking volume by service category
-- uses idx_fact_travel_category
SELECT
    category,
    COUNT(*) AS total_bookings,
    SUM(price) AS total_revenue_usd,
    ROUND(AVG(price), 2) AS avg_booking_value_usd,
    ROUND(AVG(rating), 2) AS avg_rating
FROM fact_travel_bookings
WHERE payment_status = 'COMPLETED'
GROUP BY category
ORDER BY total_revenue_usd DESC;


-- Month-over-month revenue trend
-- uses idx_fact_travel_booking_date
SELECT
    TO_CHAR(booking_date, 'YYYY-MM') AS month,
    COUNT(*) AS bookings,
    SUM(price) AS revenue_usd,
    SUM(price) - LAG(SUM(price)) OVER (ORDER BY TO_CHAR(booking_date, 'YYYY-MM')) AS mom_change_usd
FROM fact_travel_bookings
WHERE payment_status = 'COMPLETED'
GROUP BY TO_CHAR(booking_date, 'YYYY-MM')
ORDER BY month;


-- Country-level performance: revenue, avg rating, and high-satisfaction count
-- uses idx_fact_travel_country
SELECT
    country,
    COUNT(*) AS bookings,
    SUM(price) AS revenue_usd,
    ROUND(AVG(rating), 2) AS avg_rating,
    COUNT(*) FILTER (WHERE rating >= 4.5) AS five_star_bookings
FROM fact_travel_bookings
WHERE payment_status = 'COMPLETED'
GROUP BY country
ORDER BY revenue_usd DESC;
