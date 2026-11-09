package responses

import "time"

type TelemetryResponse struct {
	ID               string    `json:"id"`
	TruckPlate       string    `json:"truck_plate"`
	Latitude         float64   `json:"latitude"`
	Longitude        float64   `json:"longitude"`
	SpeedKMH         float64   `json:"speed_kmh"`
	ValveOpen        bool      `json:"valve_open"`
	FuelLevelPercent float64   `json:"fuel_level_percent"`
	AlertSecurity    bool      `json:"alert_security"`
	Timestamp        time.Time `json:"timestamp"`
}
