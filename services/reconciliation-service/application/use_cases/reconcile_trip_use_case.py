import uuid
from datetime import datetime, timezone
from domain.ports.reconciliation_repository_port import ReconciliationRepositoryPort
from domain.ports.ai_analyst_port import AIAnalystPort
from application.commands.reconcile_trip_command import ReconcileTripCommand
from domain.models.reconciliation import Reconciliation, ReconciliationStatus

class ReconcileTripUseCase:
    def __init__(self, repository: ReconciliationRepositoryPort, ai_analyst: AIAnalystPort, loss_tolerance_percent:float = -0.5):
        self._repository = repository
        self._ai_analyst = ai_analyst
        self._loss_tolerance_percent = loss_tolerance_percent

    def execute(self, command: ReconcileTripCommand)-> Reconciliation:
        variance_liters = command.received_volume - command.dispatched_volume
        variance_percent = (variance_liters / command.dispatched_volume) * 100.0

        status = ReconciliationStatus.NORMAL
        ai_result = None

        is_suspicious_loss = variance_percent < self._loss_tolerance_percent
        has_security_breach = command.valve_opened_in_transit
        if is_suspicious_loss or has_security_breach:
            status = ReconciliationStatus.INVESTIGATION_REQUIRED

            incident_context = {
                "dispatch_id": command.dispatch_id,
                "truck_plate": command.truck_plate,
                "dispatched_liters": command.dispatched_volume,
                "received_liters": command.received_volume,
                "variance_liters": round(variance_liters, 2),
                "variance_percent": round(variance_percent, 2),
                "dispatched_temp_c": command.dispatched_temp_c,
                "received_temp_c": command.received_temp_c,
                "valve_opened_in_transit": command.valve_opened_in_transit,
                "max_speed_kmh": command.max_speed_kmh,
            }

            ai_result = self._ai_analyst.analyze_discrepancy(incident_context)
            verdict_upper = ai_result.verdict.upper()
            if ai_result.confidence > 0.8 and ("FRAUD" in verdict_upper or "ROBO" in verdict_upper):
                status = ReconciliationStatus.FRAUD_SUSPECTED

        reconciliation = Reconciliation(
            id=str(uuid.uuid4()),
            dispatch_id=command.dispatch_id,
            truck_plate=command.truck_plate,
            dispatched_volume=command.dispatched_volume,
            dispatched_temp_c=command.dispatched_temp_c,
            received_volume=command.received_volume,
            received_temp_c=command.received_temp_c,
            volume_variance_liters=round(variance_liters, 2),
            volume_variance_percent=round(variance_percent, 2),
            status=status,
            ai_analysis=ai_result,
            created_at=datetime.now(timezone.utc),
        )
        self._repository.save(reconciliation)
        return reconciliation