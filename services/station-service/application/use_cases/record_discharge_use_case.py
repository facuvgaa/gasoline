import uuid
from datetime import datetime, timezone

from domain.models.discharge import Discharge
from domain.ports.repository import DischargeRepositoryPort
from application.commands.record_discharge_command import RecordDischargeCommand
from application.responses.discharge_response import DischargeResponse

class RecordDischargeUseCase:
    def __init__(self, repository: DischargeRepositoryPort):
        self._repository = repository

    def execute(self, command: RecordDischargeCommand) -> DischargeResponse:
        discharge = Discharge(
            id=str(uuid.uuid4()),
            dispatch_id=command.dispatch_id,
            station_id=command.station_id,
            tank_id=command.tank_id,
            received_volume_liters=command.received_volume_liters,
            received_temperature_c=command.received_temperature_c,
            discharged_at=datetime.now(timezone.utc),
        )

        self._repository.save(discharge)

        return DischargeResponse.model_validate(discharge)
