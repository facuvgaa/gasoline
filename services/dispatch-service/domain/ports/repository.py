from abc import ABC, abstractmethod
from typing import Optional
from domain.models.dispatch import Dispatch

class DispatchRepositoryPort(ABC):
    @abstractmethod
    def save(self, dispatch: Dispatch) -> None:
        pass

    @abstractmethod
    def find_by_id(self, dispatch_id: str) -> Optional[Dispatch]:
        pass
