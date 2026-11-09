package exceptions

import "errors"

var (
	ErrInvalidTruckPlate  = errors.New("la patente del camión es requerida")
	ErrInvalidCoordinates = errors.New("las coordenadas GPS son inválidas (lat [-90,90], lon [-180,180])")
	ErrInvalidFuelLevel   = errors.New("el nivel de combustible debe estar entre 0 y 100")
	ErrTelemetryNotFound  = errors.New("no se encontró telemetría para este camión")
)
