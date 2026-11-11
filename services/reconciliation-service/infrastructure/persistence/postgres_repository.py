from typing import Optional
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from domain.models.reconciliation import (
    Reconciliation,
    ReconciliationStatus,
    AIAnalysisResult,
    HumanReview,
)
from domain.ports.reconciliation_repository_port import ReconciliationRepositoryPort


class PostgresReconciliationRepository(ReconciliationRepositoryPort):
    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def ensure_schema(self) -> None:
        query = """
            ALTER TABLE reconciliations
            ADD COLUMN IF NOT EXISTS human_decision VARCHAR(50),
            ADD COLUMN IF NOT EXISTS auditor_notes TEXT,
            ADD COLUMN IF NOT EXISTS reviewed_by VARCHAR(100),
            ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP WITH TIME ZONE;
        """
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
            conn.commit()

    def save(self, reconciliation: Reconciliation) -> None:
        ai = reconciliation.ai_analysis
        hr = reconciliation.human_review
        query = """
            INSERT INTO reconciliations (
                id, dispatch_id, truck_plate,
                dispatched_volume, dispatched_temp_c,
                received_volume, received_temp_c,
                volume_variance_liters, volume_variance_percent,
                status, ai_verdict, ai_confidence, ai_explanation,
                ai_recommended_action, human_decision, auditor_notes,
                reviewed_by, reviewed_at, created_at
            ) VALUES (
                %(id)s, %(dispatch_id)s, %(truck_plate)s,
                %(dispatched_volume)s, %(dispatched_temp_c)s,
                %(received_volume)s, %(received_temp_c)s,
                %(volume_variance_liters)s, %(volume_variance_percent)s,
                %(status)s, %(ai_verdict)s, %(ai_confidence)s, %(ai_explanation)s,
                %(ai_recommended_action)s, %(human_decision)s, %(auditor_notes)s,
                %(reviewed_by)s, %(reviewed_at)s, %(created_at)s
            )
        """
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, {
                    "id": reconciliation.id,
                    "dispatch_id": reconciliation.dispatch_id,
                    "truck_plate": reconciliation.truck_plate,
                    "dispatched_volume": reconciliation.dispatched_volume,
                    "dispatched_temp_c": reconciliation.dispatched_temp_c,
                    "received_volume": reconciliation.received_volume,
                    "received_temp_c": reconciliation.received_temp_c,
                    "volume_variance_liters": reconciliation.volume_variance_liters,
                    "volume_variance_percent": reconciliation.volume_variance_percent,
                    "status": reconciliation.status.value,
                    "ai_verdict": ai.verdict if ai else None,
                    "ai_confidence": ai.confidence if ai else None,
                    "ai_explanation": ai.explanation if ai else None,
                    "ai_recommended_action": ai.recommended_action if ai else None,
                    "human_decision": hr.decision if hr else None,
                    "auditor_notes": hr.notes if hr else None,
                    "reviewed_by": hr.reviewed_by if hr else None,
                    "reviewed_at": hr.reviewed_at if hr else None,
                    "created_at": reconciliation.created_at,
                })
            conn.commit()

    def update(self, reconciliation: Reconciliation) -> None:
        hr = reconciliation.human_review
        query = """
            UPDATE reconciliations
            SET status = %(status)s,
                human_decision = %(human_decision)s,
                auditor_notes = %(auditor_notes)s,
                reviewed_by = %(reviewed_by)s,
                reviewed_at = %(reviewed_at)s
            WHERE id = %(id)s
        """
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, {
                    "id": reconciliation.id,
                    "status": reconciliation.status.value,
                    "human_decision": hr.decision if hr else None,
                    "auditor_notes": hr.notes if hr else None,
                    "reviewed_by": hr.reviewed_by if hr else None,
                    "reviewed_at": hr.reviewed_at if hr else None,
                })
            conn.commit()

    def find_by_id(self, reconciliation_id: str) -> Optional[Reconciliation]:
        query = """
            SELECT id, dispatch_id, truck_plate,
                   dispatched_volume, dispatched_temp_c,
                   received_volume, received_temp_c,
                   volume_variance_liters, volume_variance_percent,
                   status, ai_verdict, ai_confidence, ai_explanation,
                   ai_recommended_action, human_decision, auditor_notes,
                   reviewed_by, reviewed_at, created_at
            FROM reconciliations
            WHERE id = %(id)s
        """
        return self._fetch_one(query, {"id": reconciliation_id})

    def find_by_dispatch_id(self, dispatch_id: str) -> Optional[Reconciliation]:
        query = """
            SELECT id, dispatch_id, truck_plate,
                   dispatched_volume, dispatched_temp_c,
                   received_volume, received_temp_c,
                   volume_variance_liters, volume_variance_percent,
                   status, ai_verdict, ai_confidence, ai_explanation,
                   ai_recommended_action, human_decision, auditor_notes,
                   reviewed_by, reviewed_at, created_at
            FROM reconciliations
            WHERE dispatch_id = %(dispatch_id)s
            ORDER BY created_at DESC
            LIMIT 1
        """
        return self._fetch_one(query, {"dispatch_id": dispatch_id})

    def find_all(self, status: Optional[str] = None) -> list[Reconciliation]:
        base_query = """
            SELECT id, dispatch_id, truck_plate,
                   dispatched_volume, dispatched_temp_c,
                   received_volume, received_temp_c,
                   volume_variance_liters, volume_variance_percent,
                   status, ai_verdict, ai_confidence, ai_explanation,
                   ai_recommended_action, human_decision, auditor_notes,
                   reviewed_by, reviewed_at, created_at
            FROM reconciliations
        """
        params: dict = {}
        if status:
            base_query += " WHERE status = %(status)s"
            params["status"] = status
        base_query += " ORDER BY created_at DESC LIMIT 100"

        with self._pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(base_query, params)
                rows = cur.fetchall()
                return [self._map_row(row) for row in rows]

    def _fetch_one(self, query: str, params: dict) -> Optional[Reconciliation]:
        with self._pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, params)
                row = cur.fetchone()
                if not row:
                    return None
                return self._map_row(row)

    @staticmethod
    def _map_row(row: dict) -> Reconciliation:
        ai_analysis = None
        if row.get("ai_verdict"):
            ai_analysis = AIAnalysisResult(
                verdict=row["ai_verdict"],
                confidence=row["ai_confidence"] or 0.0,
                explanation=row["ai_explanation"] or "",
                recommended_action=row["ai_recommended_action"] or "",
            )

        human_review = None
        if row.get("human_decision"):
            human_review = HumanReview(
                decision=row["human_decision"],
                notes=row["auditor_notes"] or "",
                reviewed_by=row["reviewed_by"] or "",
                reviewed_at=row["reviewed_at"],
            )

        return Reconciliation(
            id=row["id"],
            dispatch_id=row["dispatch_id"],
            truck_plate=row["truck_plate"],
            dispatched_volume=row["dispatched_volume"],
            dispatched_temp_c=row["dispatched_temp_c"],
            received_volume=row["received_volume"],
            received_temp_c=row["received_temp_c"],
            volume_variance_liters=row["volume_variance_liters"],
            volume_variance_percent=row["volume_variance_percent"],
            status=ReconciliationStatus(row["status"]),
            ai_analysis=ai_analysis,
            human_review=human_review,
            created_at=row["created_at"],
        )
