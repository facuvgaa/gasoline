from typing import Optional
from domain.models.reconciliation import Reconciliation
from domain.ports.reconciliation_repository_port import ReconciliationRepositoryPort


class ListReconciliationsUseCase:
    def __init__(self, repository: ReconciliationRepositoryPort):
        self._repository = repository

    def execute(self, status: Optional[str] = None) -> list[Reconciliation]:
        return self._repository.find_all(status=status)
