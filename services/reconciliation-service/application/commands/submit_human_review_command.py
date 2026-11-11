from enum import Enum
from pydantic import BaseModel, Field


class HumanDecision(str, Enum):
    CONFIRMED_FRAUD = "CONFIRMED_FRAUD"
    DISMISSED_FALSE_ALARM = "DISMISSED_FALSE_ALARM"


class SubmitHumanReviewCommand(BaseModel):
    decision: HumanDecision
    auditor_notes: str = Field(..., min_length=3, description="Observaciones del auditor humano")
    reviewed_by: str = Field(..., min_length=2, description="Nombre o ID del auditor")
