import json
import logging
import os
import threading
import time
import httpx
from kafka import KafkaConsumer

from application.commands.reconcile_trip_command import ReconcileTripCommand
from application.use_cases.reconcile_trip_use_case import ReconcileTripUseCase
from domain.ports.reconciliation_repository_port import ReconciliationRepositoryPort

logger = logging.getLogger(__name__)


class DischargeEventConsumer:
    """Consumer en segundo plano que escucha eventos de descarga y dispara reconciliación + IA"""

    def __init__(
        self,
        bootstrap_servers: str,
        reconcile_uc: ReconcileTripUseCase,
        repository: ReconciliationRepositoryPort,
        topic: str = "station.discharges",
        group_id: str = "reconciliation-service-group",
    ):
        self._bootstrap_servers = bootstrap_servers
        self._reconcile_uc = reconcile_uc
        self._repository = repository
        self._topic = topic
        self._group_id = group_id
        self._dispatch_url = os.getenv("DISPATCH_SERVICE_URL", "http://dispatch-service:8080")
        self._telemetry_url = os.getenv("TELEMETRY_SERVICE_URL", "http://telemetry-service:8081")
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("🎧 Kafka consumer iniciado en tópico '%s'", self._topic)

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            consumer = None
            try:
                consumer = KafkaConsumer(
                    self._topic,
                    bootstrap_servers=self._bootstrap_servers.split(","),
                    group_id=self._group_id,
                    auto_offset_reset="latest",
                    enable_auto_commit=True,
                    consumer_timeout_ms=1000,
                    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                )
                logger.info("✅ Conectado a Kafka/Redpanda en %s", self._bootstrap_servers)

                while not self._stop_event.is_set():
                    for message in consumer:
                        if self._stop_event.is_set():
                            break
                        self._handle_event(message.value)
            except Exception as exc:
                logger.warning("Kafka consumer reintentando conexión en 3s: %s", exc)
                time.sleep(3)
            finally:
                if consumer is not None:
                    try:
                        consumer.close()
                    except Exception:
                        pass

    def _handle_event(self, payload: dict) -> None:
        if payload.get("event") != "DischargeRecorded":
            return

        dispatch_id = payload.get("dispatch_id")
        if not dispatch_id:
            return

        # Idempotencia: evitar duplicar si ya fue reconciliado
        if self._repository.find_by_dispatch_id(dispatch_id) is not None:
            logger.info("Despacho %s ya reconciliado, ignorando evento duplicado.", dispatch_id)
            return

        logger.info("📩 Evento DischargeRecorded recibido para dispatch %s", dispatch_id)

        try:
            with httpx.Client(timeout=5.0) as client:
                disp_resp = client.get(f"{self._dispatch_url}/dispatches/{dispatch_id}")
                if disp_resp.status_code != 200:
                    logger.warning(
                        "No se encontró despacho %s en dispatch-service (HTTP %s)",
                        dispatch_id,
                        disp_resp.status_code,
                    )
                    return
                dispatch_data = disp_resp.json()

                truck_plate = dispatch_data["truck_plate"]
                valve_opened = False
                max_speed = 0.0

                tel_resp = client.get(
                    f"{self._telemetry_url}/telemetry/trucks/{truck_plate}/latest"
                )
                if tel_resp.status_code == 200:
                    tel_data = tel_resp.json()
                    valve_opened = bool(tel_data.get("alert_security") or tel_data.get("valve_open"))
                    max_speed = float(tel_data.get("speed_kmh", 0.0))

            command = ReconcileTripCommand(
                dispatch_id=dispatch_id,
                truck_plate=truck_plate,
                dispatched_volume=float(dispatch_data["volume_liters"]),
                dispatched_temp_c=float(dispatch_data["temperature_c"]),
                received_volume=float(payload["received_volume_liters"]),
                received_temp_c=float(payload["received_temperature_c"]),
                valve_opened_in_transit=valve_opened,
                max_speed_kmh=max_speed,
            )

            rec = self._reconcile_uc.execute(command)
            logger.info(
                "🤖 Reconciliación automática completada para %s (%s) -> Status: %s",
                truck_plate,
                dispatch_id,
                rec.status.value,
            )
        except Exception as exc:
            logger.error("Error procesando evento de descarga %s: %s", dispatch_id, exc)
