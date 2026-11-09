CREATE TABLE IF NOT EXISTS dispatches (
    id VARCHAR(36) PRIMARY KEY,
    truck_plate VARCHAR(20) NOT NULL,
    driver_id VARCHAR(50) NOT NULL,
    fuel_type VARCHAR(30) NOT NULL,
    volume_liters DOUBLE PRECISION NOT NULL,
    temperature_c DOUBLE PRECISION NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS telemetry_pings (
    id VARCHAR(36) PRIMARY KEY,
    truck_plate VARCHAR(20) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    speed_kmh DOUBLE PRECISION NOT NULL,
    valve_open BOOLEAN NOT NULL DEFAULT FALSE,
    fuel_level_percent DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_telemetry_truck_timestamp ON telemetry_pings (truck_plate, timestamp DESC);

CREATE TABLE IF NOT EXISTS discharges (
    id VARCHAR(36) PRIMARY KEY,
    dispatch_id VARCHAR(36) NOT NULL,
    station_id VARCHAR(50) NOT NULL,
    tank_id VARCHAR(50) NOT NULL,
    received_volume_liters DOUBLE PRECISION NOT NULL,
    received_temperature_c DOUBLE PRECISION NOT NULL,
    discharged_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_discharges_dispatch_id ON discharges (dispatch_id);
