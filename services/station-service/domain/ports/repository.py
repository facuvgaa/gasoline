from abc import ABC, abstractmethod
from typing import Optional
from domain.models.discharge import Discharge

class DischargeRepositoryPort(ABC):
    @abstractmethod
    def save(self, discharge: Discharge) -> None:
        pass

    @abstractmethod
    def find_by_id(self, discharge_id: str) -> Optional[Discharge]:
        pass

    @abstractmethod
    def find_by_dispatch_id(self, dispatch_id: str) -> Optional[Discharge]:
        pass
