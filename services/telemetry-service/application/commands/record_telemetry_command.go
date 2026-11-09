package commands

import (
	"telemetry-service/domain/exceptions"
)

type RecordTelemetryCommand struct {
	TruckPlate       string  `json:"truck_plate"`
	Latitude         float64 `json:"latitude"`
	Longitude        float64 `json:"longitude"`
	SpeedKMH         float64 `json:"speed_kmh"`
	ValveOpen        bool    `json:"valve_open"`
	FuelLevelPercent float64 `json:"fuel_level_percent"`
}

func (c *RecordTelemetryCommand) Validate() error {
	if c.TruckPlate == "" {
		return exceptions.ErrInvalidTruckPlate
	}
	if c.Latitude < -90 || c.Latitude > 90 || c.Longitude < -180 || c.Longitude > 180 {
		return exceptions.ErrInvalidCoordinates
	}
	if c.FuelLevelPercent < 0 || c.FuelLevelPercent > 100 {
		return exceptions.ErrInvalidFuelLevel
	}
	return nil
}
