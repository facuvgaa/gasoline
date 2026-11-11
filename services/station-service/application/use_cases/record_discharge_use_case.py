import uuid
from datetime import datetime, timezone
from typing import Optional

from domain.models.discharge import Discharge
from domain.ports.repository import DischargeRepositoryPort
from domain.ports.event_publisher import EventPublisherPort
from application.commands.record_discharge_command import RecordDischargeCommand
from application.responses.discharge_response import DischargeResponse


class RecordDischargeUseCase:
    def __init__(
        self,
        repository: DischargeRepositoryPort,
        event_publisher: Optional[EventPublisherPort] = None,
    ):
        self._repository = repository
        self._event_publisher = event_publisher

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

        if self._event_publisher is not None:
            self._event_publisher.publish_discharge_recorded(discharge)

        return DischargeResponse.model_validate(discharge)
