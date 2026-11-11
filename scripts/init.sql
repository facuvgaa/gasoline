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

CREATE TABLE IF NOT EXISTS reconciliations (
    id VARCHAR(36) PRIMARY KEY,
    dispatch_id VARCHAR(36) NOT NULL,
    truck_plate VARCHAR(20) NOT NULL,
    dispatched_volume DOUBLE PRECISION NOT NULL,
    dispatched_temp_c DOUBLE PRECISION NOT NULL,
    received_volume DOUBLE PRECISION NOT NULL,
    received_temp_c DOUBLE PRECISION NOT NULL,
    volume_variance_liters DOUBLE PRECISION NOT NULL,
    volume_variance_percent DOUBLE PRECISION NOT NULL,
    status VARCHAR(30) NOT NULL,
    ai_verdict VARCHAR(50),
    ai_confidence DOUBLE PRECISION,
    ai_explanation TEXT,
    ai_recommended_action TEXT,
    human_decision VARCHAR(50),
    auditor_notes TEXT,
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reconciliations_dispatch_id ON reconciliations (dispatch_id);
