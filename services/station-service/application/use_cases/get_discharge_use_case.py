from domain.ports.repository import DischargeRepositoryPort
from domain.exceptions.exceptions import DischargeNotFoundException
from application.responses.discharge_response import DischargeResponse

class GetDischargeUseCase:
    def __init__(self, repository: DischargeRepositoryPort):
        self._repository = repository

    def execute_by_id(self, discharge_id: str) -> DischargeResponse:
        discharge = self._repository.find_by_id(discharge_id)
        if not discharge:
            raise DischargeNotFoundException(f"Descarga con ID {discharge_id} no encontrada")
        return DischargeResponse.model_validate(discharge)

    def execute_by_dispatch_id(self, dispatch_id: str) -> DischargeResponse:
        discharge = self._repository.find_by_dispatch_id(dispatch_id)
        if not discharge:
            raise DischargeNotFoundException(f"No se encontró descarga asociada al despacho {dispatch_id}")
        return DischargeResponse.model_validate(discharge)
