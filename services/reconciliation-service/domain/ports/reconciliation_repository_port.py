from abc import ABC, abstractmethod
from typing import Optional
from domain.models.reconciliation import Reconciliation


class ReconciliationRepositoryPort(ABC):
    """Puerto para persistir los resultados de la reconciliación"""

    @abstractmethod
    def save(self, reconciliation: Reconciliation) -> None:
        pass

    @abstractmethod
    def update(self, reconciliation: Reconciliation) -> None:
        pass

    @abstractmethod
    def find_by_id(self, reconciliation_id: str) -> Optional[Reconciliation]:
        pass

    @abstractmethod
    def find_by_dispatch_id(self, dispatch_id: str) -> Optional[Reconciliation]:
        pass

    @abstractmethod
    def find_all(self, status: Optional[str] = None) -> list[Reconciliation]:
        pass
