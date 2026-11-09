from domain.ports.repository import DispatchRepositoryPort
from domain.exceptions.exceptions import DispatchNotFoundException
from application.responses.dispatch_response import DispatchResponse

class GetDispatchUseCase:
    def __init__(self, repository: DispatchRepositoryPort):
        self._repository = repository

    def execute(self, dispatch_id: str) -> DispatchResponse:
        dispatch = self._repository.find_by_id(dispatch_id)
        if not dispatch:
            raise DispatchNotFoundException(f"Despacho con ID {dispatch_id} no encontrado")

        return DispatchResponse.model_validate(dispatch)
