CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    period VARCHAR(20) NOT NULL,
    temperature DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE VIEW weather_avg AS
SELECT 
    period,
    ROUND(AVG(temperature), 0) as avg_temp
FROM (
    SELECT DISTINCT ON (source, period) 
        source, period, temperature
    FROM weather_data
    ORDER BY source, period, created_at DESC
) latest
GROUP BY period;

INSERT INTO weather_data (source, period, temperature) VALUES
('source1', 'morning', 12),
('source2', 'morning', 11),
('source3', 'morning', 13),
('source1', 'day', 18),
('source2', 'day', 19),
('source3', 'day', 17),
('source1', 'evening', 14),
('source2', 'evening', 15),
('source3', 'evening', 13);
