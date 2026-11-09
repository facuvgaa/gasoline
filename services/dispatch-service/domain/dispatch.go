package domain

import (
	"errors"
	"time"
)

var (
	ErrNegativeVolume     = errors.New("The volume of gasoline must be greater than 0")
	ErrInvalidCompartment = errors.New("The number of compatiment is invalid")
)

type FuelType string

const (
	FuelSuper   FuelType = "NAFTA_SUPER"
	FuelPremium FuelType = "NAFTA_PREMIUM"
	FuelDiesel  FuelType = "DIESEL_500"
)

type Dispatch struct {
	ID           string    `json:"id"`
	TruckPlate   string    `json:"truct_plate"`
	DriverID     string    `json:"driver_id"`
	FuelType     FuelType  `json:"fuel_type"`
	VolumeLiters float64   `json:"volume_liters"`
	TemperatureC float64   `json:"temperature_c"`
	Status       string    `json:"status"`
	CreatedAt    time.Time `json:"created_at"`
}

func NewDispatch(id, plate, driverID string, fuel FuelType, volume, temp float64) (*Dispatch, error) {
	if volume <= 0 {
		return nil, ErrNegativeVolume
	}
	return &Dispatch{
		ID:           id,
		TruckPlate:   plate,
		DriverID:     driverID,
		FuelType:     fuel,
		VolumeLiters: volume,
		TemperatureC: temp,
		Status:       "LOADED",
		CreatedAt:    time.Now().UTC(),
	}, nil
}
