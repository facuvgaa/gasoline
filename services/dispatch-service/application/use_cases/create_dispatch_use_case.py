import uuid
from datetime import datetime, timezone

from domain.models.dispatch import Dispatch
from domain.ports.repository import DispatchRepositoryPort
from application.commands.create_dispatch_command import CreateDispatchCommand
from application.responses.dispatch_response import DispatchResponse

class CreateDispatchUseCase:
    def __init__(self, repository: DispatchRepositoryPort):
        self._repository = repository

    def execute(self, command: CreateDispatchCommand) -> DispatchResponse:
        dispatch = Dispatch(
            id=str(uuid.uuid4()),
            truck_plate=command.truck_plate,
            driver_id=command.driver_id,
            fuel_type=command.fuel_type,
            volume_liters=command.volume_liters,
            temperature_c=command.temperature_c,
            status="LOADED",
            created_at=datetime.now(timezone.utc),
        )

        self._repository.save(dispatch)

        return DispatchResponse.model_validate(dispatch)
