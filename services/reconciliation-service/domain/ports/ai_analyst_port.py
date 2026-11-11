from abc import ABC, abstractmethod
from domain.models.reconciliation import AIAnalysisResult


class AIAnalystPort(ABC):
    @abstractmethod
    def analyze_discrepancy(self, incident_context: dict) -> AIAnalysisResult:
        pass