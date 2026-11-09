package usecases

import (
	"context"
	"log"
	"time"

	"telemetry-service/application/commands"
	"telemetry-service/application/responses"
	"telemetry-service/domain/models"
	"telemetry-service/domain/ports"

	"github.com/google/uuid"
)

type RecordTelemetryUseCase struct {
	repo ports.TelemetryRepositoryPort
}

func NewRecordTelemetryUseCase(repo ports.TelemetryRepositoryPort) *RecordTelemetryUseCase {
	return &RecordTelemetryUseCase{
		repo: repo,
	}
}

func (uc *RecordTelemetryUseCase) Execute(ctx context.Context, cmd commands.RecordTelemetryCommand) (*responses.TelemetryResponse, error) {
	// 1. Validación en el límite del Command
	if err := cmd.Validate(); err != nil {
		return nil, err
	}

	// 2. Detección de alerta de seguridad en ruta (Válvula abierta en movimiento = POSIBLE ROBO)
	securityAlert := false
	if cmd.ValveOpen && cmd.SpeedKMH > 5.0 {
		securityAlert = true
		log.Printf("🚨 ALERTA CRÍTICA: Camión %s abrió válvula a %.1f km/h en lat: %.4f, lon: %.4f\n",
			cmd.TruckPlate, cmd.SpeedKMH, cmd.Latitude, cmd.Longitude)
	}

	// 3. Crear modelo de dominio
	ping := &models.TelemetryPing{
		ID:               uuid.New().String(),
		TruckPlate:       cmd.TruckPlate,
		Latitude:         cmd.Latitude,
		Longitude:        cmd.Longitude,
		SpeedKMH:         cmd.SpeedKMH,
		ValveOpen:        cmd.ValveOpen,
		FuelLevelPercent: cmd.FuelLevelPercent,
		Timestamp:        time.Now().UTC(),
	}

	// 4. Persistir a través del puerto
	if err := uc.repo.Save(ctx, ping); err != nil {
		return nil, err
	}

	return &responses.TelemetryResponse{
		ID:               ping.ID,
		TruckPlate:       ping.TruckPlate,
		Latitude:         ping.Latitude,
		Longitude:        ping.Longitude,
		SpeedKMH:         ping.SpeedKMH,
		ValveOpen:        ping.ValveOpen,
		FuelLevelPercent: ping.FuelLevelPercent,
		AlertSecurity:    securityAlert,
		Timestamp:        ping.Timestamp,
	}, nil
}
