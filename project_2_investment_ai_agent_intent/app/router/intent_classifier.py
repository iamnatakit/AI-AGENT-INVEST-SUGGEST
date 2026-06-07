from typing import Dict, Any
import os
import json
from project_2_investment_ai_agent_intent.app.llm_gateway.openrouter_client import OpenRouterClient
from project_2_investment_ai_agent_intent.app.router.intent_schema import get_intent_json_schema, IntentOutput, INTENT_JSON_INSTRUCTION

INTENT_SYSTEM_PROMPT = f"""
คุณคือผู้จำแนกประเภทคำถาม (Intent Classifier) สำหรับระบบ Investment AI Agent
วิเคราะห์ข้อความของผู้ใช้แล้วระบุ domain, ความซับซ้อน, และความต้องการเฉพาะ
คุณต้องตอบเป็น JSON ที่ถูกต้องตาม JSON schema ที่กำหนดเท่านั้น

{INTENT_JSON_INSTRUCTION}
"""

_DEFAULT_INTENT = {
    "domain": "general_finance",
    "sub_domains": [],
    "ticker": None,
    "market": None,
    "complexity": "low",
    "risk_profile_required": False,
    "needs_realtime_data": False,
    "selected_model_tier": "cheap",
    "reason": "Fallback intent — classification unavailable"
}

class IntentClassifier:
    def __init__(self, client: OpenRouterClient = None):
        self.client = client or OpenRouterClient()
        self.schema = get_intent_json_schema()

    @property
    def model(self):
        return os.getenv("INTENT_MODEL", "google/gemini-2.0-flash-001").strip()

    def classify(self, user_message: str) -> Dict[str, Any]:
        try:
            result = self.client.generate_structured_response(
                model=self.model,
                system_prompt=INTENT_SYSTEM_PROMPT,
                user_message=user_message,
                json_schema=self.schema
            )
        except Exception as e:
            # Intent classification failure must never crash the whole request
            return {
                "intent": {**_DEFAULT_INTENT, "reason": f"Classifier API error: {str(e)}"},
                "usage": {},
                "raw_response": str(e)
            }

        parsed_json = result.get("parsed_json")

        if not parsed_json:
            parsed_json = {**_DEFAULT_INTENT, "reason": "Failed to parse JSON from classifier"}

        try:
            intent_obj = IntentOutput(**parsed_json)
            validated_json = intent_obj.model_dump() if hasattr(intent_obj, "model_dump") else intent_obj.dict()
        except Exception as e:
            parsed_json["reason"] = f"Validation failed: {str(e)}"
            parsed_json["domain"] = "general_finance"
            validated_json = parsed_json

        return {
            "intent": validated_json,
            "usage": result.get("usage", {}),
            "raw_response": result.get("raw_content", "")
        }
