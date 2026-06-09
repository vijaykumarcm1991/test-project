-- Initialize database schema
CREATE TABLE IF NOT EXISTS weather_cache (
    id SERIAL PRIMARY KEY,
    city VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    temperature DECIMAL(5, 2),
    feels_like DECIMAL(5, 2),
    humidity INTEGER,
    pressure INTEGER,
    wind_speed DECIMAL(5, 2),
    wind_direction VARCHAR(50),
    condition VARCHAR(100),
    visibility DECIMAL(5, 2),
    dew_point DECIMAL(5, 2),
    uv_index DECIMAL(3, 2),
    sunrise TIME,
    sunset TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS search_history (
    id SERIAL PRIMARY KEY,
    query VARCHAR(255) NOT NULL,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_weather_cache_city ON weather_cache(city);
CREATE INDEX IF NOT EXISTS idx_search_history_created ON search_history(created_at);

-- Insert some sample data for demo mode
INSERT INTO weather_cache (city, country, temperature, feels_like, humidity, pressure, wind_speed, wind_direction, condition, visibility, dew_point, uv_index, sunrise, sunset)
VALUES 
    ('London', 'UK', 15.5, 14.2, 72, 1013, 18.5, 'SW', 'Partly Cloudy', 10.0, 10.5, 3.5, '06:45', '18:30'),
    ('New York', 'USA', 22.3, 23.1, 65, 1015, 12.0, 'W', 'Sunny', 15.0, 15.2, 5.2, '06:15', '19:45'),
    ('Tokyo', 'Japan', 18.7, 19.5, 78, 1010, 8.5, 'SE', 'Cloudy', 8.0, 14.8, 2.8, '05:30', '18:00'),
    ('Paris', 'France', 16.2, 15.8, 68, 1012, 15.0, 'NW', 'Light Rain', 6.0, 10.2, 2.0, '07:00', '19:15'),
    ('Sydney', 'Australia', 25.8, 27.2, 55, 1018, 22.0, 'E', 'Sunny', 20.0, 16.5, 7.5, '06:00', '17:30')
ON CONFLICT DO NOTHING;
