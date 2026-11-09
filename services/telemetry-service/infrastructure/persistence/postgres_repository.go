package persistence

import (
	"context"
	"errors"

	"telemetry-service/domain/models"
	"telemetry-service/domain/ports"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type PostgresTelemetryRepository struct {
	pool *pgxpool.Pool
}

var _ ports.TelemetryRepositoryPort = (*PostgresTelemetryRepository)(nil)

func NewPostgresTelemetryRepository(pool *pgxpool.Pool) *PostgresTelemetryRepository {
	return &PostgresTelemetryRepository{
		pool: pool,
	}
}

func (r *PostgresTelemetryRepository) Save(ctx context.Context, ping *models.TelemetryPing) error {
	query := `
		INSERT INTO telemetry_pings (
			id, truck_plate, latitude, longitude,
			speed_kmh, valve_open, fuel_level_percent, timestamp
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
	`
	_, err := r.pool.Exec(ctx, query,
		ping.ID,
		ping.TruckPlate,
		ping.Latitude,
		ping.Longitude,
		ping.SpeedKMH,
		ping.ValveOpen,
		ping.FuelLevelPercent,
		ping.Timestamp,
	)
	return err
}

func (r *PostgresTelemetryRepository) FindLatestByTruck(ctx context.Context, truckPlate string) (*models.TelemetryPing, error) {
	query := `
		SELECT id, truck_plate, latitude, longitude, speed_kmh, valve_open, fuel_level_percent, timestamp
		FROM telemetry_pings
		WHERE truck_plate = $1
		ORDER BY timestamp DESC
		LIMIT 1
	`
	row := r.pool.QueryRow(ctx, query, truckPlate)

	var p models.TelemetryPing
	err := row.Scan(
		&p.ID,
		&p.TruckPlate,
		&p.Latitude,
		&p.Longitude,
		&p.SpeedKMH,
		&p.ValveOpen,
		&p.FuelLevelPercent,
		&p.Timestamp,
	)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return nil, nil
		}
		return nil, err
	}
	return &p, nil
}
