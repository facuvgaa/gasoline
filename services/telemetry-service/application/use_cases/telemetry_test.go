package usecases_test

import (
	"context"
	"testing"

	"telemetry-service/application/commands"
	usecases "telemetry-service/application/use_cases"
	"telemetry-service/domain/exceptions"
	"telemetry-service/domain/models"
	"telemetry-service/domain/ports"
)

// FakeTelemetryRepository implementa ports.TelemetryRepositoryPort en memoria
type FakeTelemetryRepository struct {
	pings map[string][]*models.TelemetryPing
}

var _ ports.TelemetryRepositoryPort = (*FakeTelemetryRepository)(nil)

func NewFakeTelemetryRepository() *FakeTelemetryRepository {
	return &FakeTelemetryRepository{
		pings: make(map[string][]*models.TelemetryPing),
	}
}

func (f *FakeTelemetryRepository) Save(ctx context.Context, ping *models.TelemetryPing) error {
	f.pings[ping.TruckPlate] = append(f.pings[ping.TruckPlate], ping)
	return nil
}

func (f *FakeTelemetryRepository) FindLatestByTruck(ctx context.Context, truckPlate string) (*models.TelemetryPing, error) {
	list, exists := f.pings[truckPlate]
	if !exists || len(list) == 0 {
		return nil, nil
	}
	return list[len(list)-1], nil
}

func TestRecordTelemetry_Success(t *testing.T) {
	repo := NewFakeTelemetryRepository()
	uc := usecases.NewRecordTelemetryUseCase(repo)

	cmd := commands.RecordTelemetryCommand{
		TruckPlate:       "AF123ZZ",
		Latitude:         -34.6037,
		Longitude:        -58.3816,
		SpeedKMH:         60.0,
		ValveOpen:        false,
		FuelLevelPercent: 95.0,
	}

	res, err := uc.Execute(context.Background(), cmd)
	if err != nil {
		t.Fatalf("se esperaba éxito, pero dio error: %v", err)
	}

	if res.ID == "" {
		t.Errorf("se esperaba un ID generado")
	}
	if res.AlertSecurity {
		t.Errorf("no debería disparar alerta de seguridad si la válvula está cerrada")
	}
}

func TestRecordTelemetry_SecurityAlert_WhenValveOpensInMovement(t *testing.T) {
	repo := NewFakeTelemetryRepository()
	uc := usecases.NewRecordTelemetryUseCase(repo)

	// Camión a 70 km/h con válvula abierta -> ALERTA DE ROBO
	cmd := commands.RecordTelemetryCommand{
		TruckPlate:       "AF123ZZ",
		Latitude:         -34.6037,
		Longitude:        -58.3816,
		SpeedKMH:         70.0,
		ValveOpen:        true,
		FuelLevelPercent: 90.0,
	}

	res, err := uc.Execute(context.Background(), cmd)
	if err != nil {
		t.Fatalf("error inesperado: %v", err)
	}

	if !res.AlertSecurity {
		t.Errorf("se esperaba AlertSecurity = true al abrir la válvula en movimiento")
	}
}

func TestRecordTelemetry_FailsOnInvalidCoordinates(t *testing.T) {
	repo := NewFakeTelemetryRepository()
	uc := usecases.NewRecordTelemetryUseCase(repo)

	cmd := commands.RecordTelemetryCommand{
		TruckPlate:       "AF123ZZ",
		Latitude:         999.0, // Latitud imposible
		Longitude:        -58.0,
		SpeedKMH:         0.0,
		ValveOpen:        false,
		FuelLevelPercent: 50.0,
	}

	_, err := uc.Execute(context.Background(), cmd)
	if err == nil {
		t.Fatalf("se esperaba error por coordenadas inválidas, pero pasó")
	}
	if err != exceptions.ErrInvalidCoordinates {
		t.Errorf("se esperaba ErrInvalidCoordinates, se obtuvo: %v", err)
	}
}
