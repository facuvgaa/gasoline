from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class ReconciliationStatus(str, Enum):
    NORMAL = "NORMAL"
    INVESTIGATION_REQUIRED = "INVESTIGATION_REQUIRED"
    FRAUD_SUSPECTED = "FRAUD_SUSPECTED"
    CONFIRMED_FRAUD = "CONFIRMED_FRAUD"
    DISMISSED_FALSE_ALARM = "DISMISSED_FALSE_ALARM"


@dataclass
class AIAnalysisResult:
    """Lo que devuelve AWS Bedrock cuando analiza el incidente"""
    verdict: str
    confidence: float
    explanation: str
    recommended_action: str


@dataclass
class HumanReview:
    """Decisión tomada por el auditor Human-in-the-Loop"""
    decision: str
    notes: str
    reviewed_by: str
    reviewed_at: datetime


@dataclass
class Reconciliation:
    """Entidad raíz del Dominio"""
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
    ai_analysis: Optional[AIAnalysisResult] = None
    human_review: Optional[HumanReview] = None
    created_at: Optional[datetime] = None
