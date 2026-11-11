import json
import logging
from typing import Optional
from kafka import KafkaProducer

from domain.models.discharge import Discharge
from domain.ports.event_publisher import EventPublisherPort

logger = logging.getLogger(__name__)


class KafkaEventPublisher(EventPublisherPort):
    def __init__(self, bootstrap_servers: str, topic: str = "station.discharges"):
        self._bootstrap_servers = bootstrap_servers
        self._topic = topic
        self._producer: Optional[KafkaProducer] = None

    def _get_producer(self) -> KafkaProducer:
        if self._producer is None:
            self._producer = KafkaProducer(
                bootstrap_servers=self._bootstrap_servers.split(","),
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
            )
        return self._producer

    def publish_discharge_recorded(self, discharge: Discharge) -> None:
        event_payload = {
            "event": "DischargeRecorded",
            "discharge_id": discharge.id,
            "dispatch_id": discharge.dispatch_id,
            "station_id": discharge.station_id,
            "tank_id": discharge.tank_id,
            "received_volume_liters": discharge.received_volume_liters,
            "received_temperature_c": discharge.received_temperature_c,
            "discharged_at": discharge.discharged_at.isoformat(),
        }
        try:
            producer = self._get_producer()
            future = producer.send(
                self._topic,
                key=discharge.dispatch_id,
                value=event_payload,
            )
            future.get(timeout=5)
            logger.info("📤 Evento DischargeRecorded publicado para dispatch %s", discharge.dispatch_id)
        except Exception as exc:
            logger.warning("No se pudo publicar evento en Kafka (%s): %s", self._topic, exc)

    def close(self) -> None:
        if self._producer is not None:
            self._producer.close()
            self._producer = None
