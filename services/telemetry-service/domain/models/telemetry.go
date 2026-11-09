package models

import "time"

// TelemetryPing es el modelo puro de datos que emite el sensor IoT del camión cisterna
type TelemetryPing struct {
	ID               string    `json:"id"`
	TruckPlate       string    `json:"truck_plate"`
	Latitude         float64   `json:"latitude"`
	Longitude        float64   `json:"longitude"`
	SpeedKMH         float64   `json:"speed_kmh"`
	ValveOpen        bool      `json:"valve_open"` // Válvula de seguridad: true si está abierta
	FuelLevelPercent float64   `json:"fuel_level_percent"`
	Timestamp        time.Time `json:"timestamp"`
}
