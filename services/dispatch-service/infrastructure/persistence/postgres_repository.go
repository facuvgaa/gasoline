package persistence

import (
	"context"
	"dispatch-service/domain"
	"errors"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type PostgresDispatchRepository struct {
	pool *pgxpool.Pool
}

func NewPostgresDispatchRepository(pool *pgxpool.Pool) *PostgresDispatchRepository {
	return &PostgresDispatchRepository{
		pool: pool,
	}
}
func (r *PostgresDispatchRepository) Save(ctx context.Context, d *domain.Dispatch) error {
	query := `
		INSERT INTO dispatches (id, truck_plate, driver_id, fuel_type, volume_liters, temperature_c, status, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
	`
	_, err := r.pool.Exec(ctx, query,
		d.ID,
		d.TruckPlate,
		d.DriverID,
		string(d.FuelType),
		d.VolumeLiters,
		d.TemperatureC,
		d.Status,
		d.CreatedAt,
	)
	return err
}
func (r *PostgresDispatchRepository) FindByID(ctx context.Context, id string) (*domain.Dispatch, error) {
	query := `
		SELECT id, truck_plate, driver_id, fuel_type, volume_liters, temperature_c, status, created_at
		FROM dispatches
		WHERE id = $1
	`
	row := r.pool.QueryRow(ctx, query, id)
	var d domain.Dispatch
	var fuel string

	err := row.Scan(
		&d.ID,
		&d.TruckPlate,
		&d.DriverID,
		&fuel,
		&d.VolumeLiters,
		&d.TemperatureC,
		&d.Status,
		&d.CreatedAt,
	)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return nil, errors.New("despacho no encontrado")
		}
		return nil, err
	}
	d.FuelType = domain.FuelType(fuel)
	return &d, nil
}
