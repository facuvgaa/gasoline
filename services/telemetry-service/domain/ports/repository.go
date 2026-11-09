package ports

import (
	"context"
	"telemetry-service/domain/models"
)

type TelemetryRepositoryPort interface {
	Save(ctx context.Context, ping *models.TelemetryPing) error
	FindLatestByTruck(ctx context.Context, truckPlate string) (*models.TelemetryPing, error)
}
