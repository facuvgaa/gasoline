from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from domain.models.reconciliation import ReconciliationStatus


class AIAnalysisResponse(BaseModel):
    verdict: str
    confidence: float
    explanation: str
    recommended_action: str

    model_config = ConfigDict(from_attributes=True)


class HumanReviewResponse(BaseModel):
    decision: str
    notes: str
    reviewed_by: str
    reviewed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReconciliationResponse(BaseModel):
    id: str
    dispatch_id: str
    truck_plate: str
    dispatched_volume: float
    dispatched_temp_c: float
    received_volume: float
    received_temp_c: float
    volume_variance_liters: float
    volume_variance_percent: float
    status: ReconciliationStatus
    ai_analysis: Optional[AIAnalysisResponse] = None
    human_review: Optional[HumanReviewResponse] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
