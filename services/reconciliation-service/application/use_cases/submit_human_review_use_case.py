from datetime import datetime, timezone

from domain.models.reconciliation import Reconciliation, ReconciliationStatus, HumanReview
from domain.ports.reconciliation_repository_port import ReconciliationRepositoryPort
from domain.exceptions.exceptions import ReconciliationNotFoundException
from application.commands.submit_human_review_command import SubmitHumanReviewCommand, HumanDecision


class SubmitHumanReviewUseCase:
    def __init__(self, repository: ReconciliationRepositoryPort):
        self._repository = repository

    def execute(self, reconciliation_id: str, command: SubmitHumanReviewCommand) -> Reconciliation:
        reconciliation = self._repository.find_by_id(reconciliation_id)
        if not reconciliation:
            raise ReconciliationNotFoundException(
                f"Reconciliación con ID {reconciliation_id} no encontrada"
            )

        reconciliation.human_review = HumanReview(
            decision=command.decision.value,
            notes=command.auditor_notes,
            reviewed_by=command.reviewed_by,
            reviewed_at=datetime.now(timezone.utc),
        )

        if command.decision == HumanDecision.CONFIRMED_FRAUD:
            reconciliation.status = ReconciliationStatus.CONFIRMED_FRAUD
        else:
            reconciliation.status = ReconciliationStatus.DISMISSED_FALSE_ALARM

        self._repository.update(reconciliation)
        return reconciliation
