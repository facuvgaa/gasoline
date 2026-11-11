from abc import ABC, abstractmethod
from domain.models.discharge import Discharge


class EventPublisherPort(ABC):
    """Puerto de salida para publicar eventos de dominio al bus (Kafka / Redpanda)"""

    @abstractmethod
    def publish_discharge_recorded(self, discharge: Discharge) -> None:
        pass
