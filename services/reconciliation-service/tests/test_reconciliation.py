import pytest

from domain.models.reconciliation import ReconciliationStatus, AIAnalysisResult
from domain.ports.reconciliation_repository_port import ReconciliationRepositoryPort
from domain.ports.ai_analyst_port import AIAnalystPort
from application.commands.reconcile_trip_command import ReconcileTripCommand
from application.commands.submit_human_review_command import (
    SubmitHumanReviewCommand,
    HumanDecision,
)
from application.use_cases.reconcile_trip_use_case import ReconcileTripUseCase
from application.use_cases.submit_human_review_use_case import SubmitHumanReviewUseCase
from application.use_cases.list_reconciliations_use_case import ListReconciliationsUseCase


class FakeRepo(ReconciliationRepositoryPort):
    def __init__(self):
        self.items = {}

    def save(self, reconciliation):
        self.items[reconciliation.id] = reconciliation

    def update(self, reconciliation):
        self.items[reconciliation.id] = reconciliation

    def find_by_id(self, reconciliation_id):
        return self.items.get(reconciliation_id)

    def find_by_dispatch_id(self, dispatch_id):
        for r in self.items.values():
            if r.dispatch_id == dispatch_id:
                return r
        return None

    def find_all(self, status=None):
        res = list(self.items.values())
        if status:
            res = [r for r in res if r.status.value == status]
        return res


class FakeAI(AIAnalystPort):
    def analyze_discrepancy(self, incident_context):
        return AIAnalysisResult(
            verdict="FRAUDE_SOSPECHADO",
            confidence=0.95,
            explanation="Válvula abierta en ruta",
            recommended_action="Bloquear chofer",
        )


def test_reconcile_normal():
    repo = FakeRepo()
    uc = ReconcileTripUseCase(repo, FakeAI())
    cmd = ReconcileTripCommand(
        dispatch_id="d1",
        truck_plate="P1",
        dispatched_volume=1000.0,
        dispatched_temp_c=17.0,
        received_volume=999.0,
        received_temp_c=20.0,
    )
    r = uc.execute(cmd)
    assert r.status == ReconciliationStatus.NORMAL
    assert r.volume_variance_liters == -1.0


def test_reconcile_fraud_suspected_and_human_review():
    repo = FakeRepo()
    reconcile_uc = ReconcileTripUseCase(repo, FakeAI())
    review_uc = SubmitHumanReviewUseCase(repo)
    list_uc = ListReconciliationsUseCase(repo)

    cmd = ReconcileTripCommand(
        dispatch_id="d2",
        truck_plate="P2",
        dispatched_volume=1000.0,
        dispatched_temp_c=17.0,
        received_volume=900.0,
        received_temp_c=20.0,
        valve_opened_in_transit=True,
        max_speed_kmh=60.0,
    )
    rec = reconcile_uc.execute(cmd)
    assert rec.status == ReconciliationStatus.FRAUD_SUSPECTED

    # Listar pendientes
    pending = list_uc.execute(status="FRAUD_SUSPECTED")
    assert len(pending) == 1

    # Decisión Human-in-the-Loop
    review_cmd = SubmitHumanReviewCommand(
        decision=HumanDecision.CONFIRMED_FRAUD,
        auditor_notes="Se verificó cámara de ruta y precinto roto",
        reviewed_by="auditor.facu",
    )
    reviewed = review_uc.execute(rec.id, review_cmd)
    assert reviewed.status == ReconciliationStatus.CONFIRMED_FRAUD
    assert reviewed.human_review is not None
    assert reviewed.human_review.reviewed_by == "auditor.facu"


class FakeThermalAI(AIAnalystPort):
    def analyze_discrepancy(self, incident_context):
        return AIAnalysisResult(
            verdict="DESVIO_TERMICO",
            confidence=0.92,
            explanation="Contracción térmica por caída de temperatura",
            recommended_action="Aplicar corrección ASTM a 15°C",
        )


def test_reconcile_thermal_deviation_stays_investigation_required():
    repo = FakeRepo()
    uc = ReconcileTripUseCase(repo, FakeThermalAI())
    cmd = ReconcileTripCommand(
        dispatch_id="d3",
        truck_plate="P3",
        dispatched_volume=28000.0,
        dispatched_temp_c=24.0,
        received_volume=27620.0,
        received_temp_c=8.0,
        valve_opened_in_transit=False,
        max_speed_kmh=75.0,
    )
    rec = uc.execute(cmd)
    assert rec.status == ReconciliationStatus.INVESTIGATION_REQUIRED
    assert rec.ai_analysis.verdict == "DESVIO_TERMICO"
