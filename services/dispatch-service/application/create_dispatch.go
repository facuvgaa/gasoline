package application

import (
	"context"
	"dispatch-service/domain"

	"github.com/google/uuid"
)

type CreateDispatchInput struct {
	TruckPlate   string          `json:"truck_plate"`
	DriverID     string          `json:"driver_id"`
	FuelType     domain.FuelType `json:"fuel_type"`
	VolumeLiters float64         `json:"volume_liters"`
	TemperatureC float64         `json:"temperature_c"`
}

type CreateDispatchUseCase struct {
	repo domain.DispatchRepository
}

func NewCreateDispatchUseCase(repo domain.DispatchRepository) *CreateDispatchUseCase {
	return &CreateDispatchUseCase{
		repo: repo,
	}
}

func (uc *CreateDispatchUseCase) Execute(ctx context.Context, input CreateDispatchInput) (*domain.Dispatch, error) {

	id := uuid.New().String()

	dispatch, err := domain.NewDispatch(
		id,
		input.TruckPlate,
		input.DriverID,
		input.FuelType,
		input.VolumeLiters,
		input.TemperatureC,
	)
	if err != nil {

		return nil, err
	}

	if err := uc.repo.Save(ctx, dispatch); err != nil {
		return nil, err
	}

	return dispatch, nil
}
