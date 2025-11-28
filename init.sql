-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Справочник источников погоды
CREATE TABLE IF NOT EXISTS weather_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Справочник периодов дня
CREATE TABLE IF NOT EXISTS weather_periods (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) UNIQUE NOT NULL
);

-- Таблица данных погоды (нормализованная)
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES weather_sources(id),
    period_id INTEGER NOT NULL REFERENCES weather_periods(id),
    temperature DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Заполнение справочников
INSERT INTO weather_sources (name) VALUES ('open-meteo'), ('7timer') ON CONFLICT (name) DO NOTHING;
INSERT INTO weather_periods (name) VALUES ('morning'), ('day'), ('evening') ON CONFLICT (name) DO NOTHING;

-- Представление для усреднения (с JOIN)
CREATE OR REPLACE VIEW weather_avg AS
SELECT 
    p.name as period,
    ROUND(AVG(wd.temperature), 0) as avg_temp
FROM (
    SELECT DISTINCT ON (source_id, period_id) 
        source_id, period_id, temperature
    FROM weather_data
    ORDER BY source_id, period_id, created_at DESC
) wd
JOIN weather_periods p ON wd.period_id = p.id
GROUP BY p.name;
