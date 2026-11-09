package usecases

import (
	"context"

	"telemetry-service/application/responses"
	"telemetry-service/domain/exceptions"
	"telemetry-service/domain/ports"
)

type GetLatestTelemetryUseCase struct {
	repo ports.TelemetryRepositoryPort
}

func NewGetLatestTelemetryUseCase(repo ports.TelemetryRepositoryPort) *GetLatestTelemetryUseCase {
	return &GetLatestTelemetryUseCase{
		repo: repo,
	}
}

func (uc *GetLatestTelemetryUseCase) Execute(ctx context.Context, truckPlate string) (*responses.TelemetryResponse, error) {
	if truckPlate == "" {
		return nil, exceptions.ErrInvalidTruckPlate
	}

	ping, err := uc.repo.FindLatestByTruck(ctx, truckPlate)
	if err != nil {
		return nil, err
	}
	if ping == nil {
		return nil, exceptions.ErrTelemetryNotFound
	}

	return &responses.TelemetryResponse{
		ID:               ping.ID,
		TruckPlate:       ping.TruckPlate,
		Latitude:         ping.Latitude,
		Longitude:        ping.Longitude,
		SpeedKMH:         ping.SpeedKMH,
		ValveOpen:        ping.ValveOpen,
		FuelLevelPercent: ping.FuelLevelPercent,
		AlertSecurity:    ping.ValveOpen && ping.SpeedKMH > 5.0,
		Timestamp:        ping.Timestamp,
	}, nil
}
