from typing import Optional
from fastapi import APIRouter, status

from application.commands.reconcile_trip_command import ReconcileTripCommand
from application.commands.submit_human_review_command import SubmitHumanReviewCommand
from application.responses.reconciliation_response import (
    ReconciliationResponse,
    AIAnalysisResponse,
    HumanReviewResponse,
)
from application.use_cases.reconcile_trip_use_case import ReconcileTripUseCase
from application.use_cases.get_reconciliation_use_case import GetReconciliationUseCase
from application.use_cases.list_reconciliations_use_case import ListReconciliationsUseCase
from application.use_cases.submit_human_review_use_case import SubmitHumanReviewUseCase
from domain.models.reconciliation import Reconciliation


def create_reconciliation_router(
    reconcile_uc: ReconcileTripUseCase,
    get_uc: GetReconciliationUseCase,
    list_uc: ListReconciliationsUseCase,
    review_uc: SubmitHumanReviewUseCase,
) -> APIRouter:
    router = APIRouter(prefix="/reconciliations", tags=["Reconciliations"])

    @router.post("", response_model=ReconciliationResponse, status_code=status.HTTP_201_CREATED)
    def reconcile(command: ReconcileTripCommand) -> ReconciliationResponse:
        rec: Reconciliation = reconcile_uc.execute(command)
        return _to_response(rec)

    @router.get("", response_model=list[ReconciliationResponse])
    def list_reconciliations(status: Optional[str] = None) -> list[ReconciliationResponse]:
        items = list_uc.execute(status=status)
        return [_to_response(rec) for rec in items]

    @router.get("/{reconciliation_id}", response_model=ReconciliationResponse)
    def get_by_id(reconciliation_id: str) -> ReconciliationResponse:
        rec = get_uc.execute_by_id(reconciliation_id)
        return _to_response(rec)

    @router.get("/by-dispatch/{dispatch_id}", response_model=ReconciliationResponse)
    def get_by_dispatch(dispatch_id: str) -> ReconciliationResponse:
        rec = get_uc.execute_by_dispatch_id(dispatch_id)
        return _to_response(rec)

    @router.post("/{reconciliation_id}/review", response_model=ReconciliationResponse)
    def submit_human_review(
        reconciliation_id: str,
        command: SubmitHumanReviewCommand,
    ) -> ReconciliationResponse:
        rec = review_uc.execute(reconciliation_id, command)
        return _to_response(rec)

    return router


def _to_response(rec: Reconciliation) -> ReconciliationResponse:
    ai = None
    if rec.ai_analysis is not None:
        ai = AIAnalysisResponse(
            verdict=rec.ai_analysis.verdict,
            confidence=rec.ai_analysis.confidence,
            explanation=rec.ai_analysis.explanation,
            recommended_action=rec.ai_analysis.recommended_action,
        )

    hr = None
    if rec.human_review is not None:
        hr = HumanReviewResponse(
            decision=rec.human_review.decision,
            notes=rec.human_review.notes,
            reviewed_by=rec.human_review.reviewed_by,
            reviewed_at=rec.human_review.reviewed_at,
        )

    return ReconciliationResponse(
        id=rec.id,
        dispatch_id=rec.dispatch_id,
        truck_plate=rec.truck_plate,
        dispatched_volume=rec.dispatched_volume,
        dispatched_temp_c=rec.dispatched_temp_c,
        received_volume=rec.received_volume,
        received_temp_c=rec.received_temp_c,
        volume_variance_liters=rec.volume_variance_liters,
        volume_variance_percent=rec.volume_variance_percent,
        status=rec.status,
        ai_analysis=ai,
        human_review=hr,
        created_at=rec.created_at,
    )
