from domain.ports.reconciliation_repository_port import ReconciliationRepositoryPort
from domain.exceptions.exceptions import ReconciliationNotFoundException
from domain.models.reconciliation import Reconciliation


class GetReconciliationUseCase:
    def __init__(self, repository: ReconciliationRepositoryPort):
        self._repository = repository

    def execute_by_id(self, reconciliation_id: str) -> Reconciliation:
        rec = self._repository.find_by_id(reconciliation_id)
        if not rec:
            raise ReconciliationNotFoundException(
                f"Reconciliación con ID {reconciliation_id} no encontrada"
            )
        return rec

    def execute_by_dispatch_id(self, dispatch_id: str) -> Reconciliation:
        rec = self._repository.find_by_dispatch_id(dispatch_id)
        if not rec:
            raise ReconciliationNotFoundException(
                f"No se encontró reconciliación para el despacho {dispatch_id}"
            )
        return rec
