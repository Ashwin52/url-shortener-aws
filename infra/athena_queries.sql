-- Create database
CREATE DATABASE IF NOT EXISTS url_analytics;

-- Create table
CREATE EXTERNAL TABLE IF NOT EXISTS url_analytics.click_events (
    short_code STRING,
    long_url STRING,
    ip STRING,
    timestamp BIGINT
)
PARTITIONED BY (year INT, month INT, day INT)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://url-shortener-analytics-ashwin/clicks/'
TBLPROPERTIES ('has_encrypted_data'='false');

-- Load partitions
MSCK REPAIR TABLE url_analytics.click_events;

-- Query 1: All click events
SELECT * FROM url_analytics.click_events LIMIT 10;

-- Query 2: Total clicks per URL
SELECT short_code, COUNT(*) as total_clicks 
FROM url_analytics.click_events 
GROUP BY short_code 
ORDER BY total_clicks DESC;

-- Query 3: Clicks per day
SELECT day, month, year, COUNT(*) as clicks
FROM url_analytics.click_events
GROUP BY year, month, day
ORDER BY year, month, day;
