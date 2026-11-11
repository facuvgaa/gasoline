import os
import json
import logging
from typing import Any

from openai import OpenAI

from domain.models.reconciliation import AIAnalysisResult
from domain.ports.ai_analyst_port import AIAnalystPort

logger = logging.getLogger(__name__)


class BedrockAIAnalystAdapter(AIAnalystPort):
    """Adapter que usa AWS Bedrock Mantle (API compatible con OpenAI) para analizar discrepancias."""

    def __init__(
        self,
        model_id: str | None = None,
        region: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.model_id = model_id or os.getenv(
            "BEDROCK_MODEL_ID", "openai.gpt-oss-120b"
        )
        self.api_key = (
            api_key
            or os.getenv("AWS_BEARER_TOKEN_BEDROCK")
            or os.getenv("AWS_BEDROCK_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or ""
        )
        self.base_url = base_url or os.getenv(
            "BEDROCK_BASE_URL",
            f"https://bedrock-mantle.{self.region}.api.aws/v1",
        )
        self._client: Any = None

    def _client_lazy(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def analyze_discrepancy(self, incident_context: dict) -> AIAnalysisResult:
        prompt = self._build_prompt(incident_context)

        if not self.api_key:
            logger.warning("No se configuró API key de Bedrock; se omite análisis IA")
            return AIAnalysisResult(
                verdict="INCONCLUSIVE",
                confidence=0.0,
                explanation="API key de Bedrock no configurada",
                recommended_action="Revisión manual del incidente",
            )

        try:
            client = self._client_lazy()
            completion = client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            text = completion.choices[0].message.content or ""
            parsed = self._parse_json(text)
            raw_action = parsed.get("recommended_action", "")
            if isinstance(raw_action, list):
                raw_action = " | ".join(str(x) for x in raw_action)
            return AIAnalysisResult(
                verdict=str(parsed.get("verdict", "INCONCLUSIVE"))[:50],
                confidence=float(parsed.get("confidence", 0.0)),
                explanation=str(parsed.get("explanation", "")),
                recommended_action=str(raw_action),
            )
        except Exception as exc:  # noqa: BLE001 - degradación elegante
            logger.warning("Bedrock Mantle no disponible o respuesta inválida: %s", exc)
            return AIAnalysisResult(
                verdict="INCONCLUSIVE",
                confidence=0.0,
                explanation=f"LLM no disponible: {exc}",
                recommended_action="Revisión manual del incidente",
            )

    @staticmethod
    def _build_prompt(ctx: dict) -> str:
        return (
            "Eres un perito analista de seguridad y mermas de combustible. "
            "Analiza el siguiente incidente y responde SOLO con un JSON válido con exactamente estas claves: "
            "verdict (string corto en mayúsculas, ej: FRAUDE_SOSPECHADO, DESVIO_TERMICO o FALLA_SENSOR), "
            "confidence (número float entre 0.0 y 1.0), "
            "explanation (string conciso explicando el porqué físico y de telemetría), "
            "recommended_action (string único con la acción concreta recomendada).\n\n"
            f"Incidente: {json.dumps(ctx, ensure_ascii=False)}"
        )

    @staticmethod
    def _parse_json(text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start : end + 1]
        return json.loads(text)
