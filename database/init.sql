CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS measurements (
    id BIGSERIAL PRIMARY KEY,
    station_code VARCHAR(100) NOT NULL,
    measured_at TIMESTAMPTZ NOT NULL,
    pm25 DOUBLE PRECISION,
    pm10 DOUBLE PRECISION,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    pressure DOUBLE PRECISION,
    source VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (station_code, measured_at)
);

CREATE TABLE IF NOT EXISTS forecasts (
    id BIGSERIAL PRIMARY KEY,
    station_code VARCHAR(100) NOT NULL,
    forecast_at TIMESTAMPTZ NOT NULL,
    pm25_forecast DOUBLE PRECISION,
    pm10_forecast DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (station_code, forecast_at)
);

CREATE TABLE IF NOT EXISTS knowledge_base (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    source VARCHAR(100),
    embedding VECTOR(384),
    created_at TIMESTAMPTZ DEFAULT NOW()
);