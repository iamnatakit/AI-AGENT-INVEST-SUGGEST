import os
import json
import requests
from typing import Dict, Any, Optional

class OpenRouterClient:
    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1"

    @property
    def api_key(self):
        return os.getenv("OPENROUTER_API_KEY", "")

    @property
    def is_production(self):
        return os.getenv("ENVIRONMENT", "development") == "production"

    @property
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://investment-ai-agent.local",
            "X-Title": "Investment AI Agent (Intent Optimized)"
        }

    def generate_structured_response(self, model: str, system_prompt: str, user_message: str, json_schema: Any = None) -> Dict[str, Any]:
        if not self.api_key:
            if self.is_production:
                raise RuntimeError("OPENROUTER_API_KEY is not set. Cannot run in production without a valid API key.")
            return self._mock_response(user_message)

        # ใช้ json_object ซึ่งรองรับ Gemini บน OpenRouter (ไม่ใช้ json_schema strict)
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers,
                json=payload,
                timeout=30
            )
            if not response.ok:
                error_detail = response.text
                if self.is_production:
                    pass # Intent classifier should never crash
                return {"parsed_json": None, "raw_content": f"API Error {response.status_code}: {error_detail}", "usage": {}, "error": True}
            
            data = response.json()

            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})

            try:
                parsed_json = json.loads(content)
            except json.JSONDecodeError:
                parsed_json = None

            return {
                "parsed_json": parsed_json,
                "raw_content": content,
                "usage": usage
            }
        except requests.exceptions.Timeout:
            # Intent classifier timeout — ใช้ fallback ไม่ crash
            return {"parsed_json": None, "raw_content": "timeout", "usage": {}, "error": True}
        except Exception as e:
            # Intent classifier error — ใช้ fallback ไม่ crash
            return {"parsed_json": None, "raw_content": str(e), "usage": {}, "error": True}


    def generate_text_response(self, model: str, system_prompt: str, user_message: str) -> Dict[str, Any]:
        if not self.api_key:
            if self.is_production:
                raise RuntimeError("OPENROUTER_API_KEY is not set. Cannot run in production without a valid API key.")
            return {
                "content": f"[DEV MOCK] ได้รับคำถาม: '{user_message}' — กรุณาตั้งค่า OPENROUTER_API_KEY",
                "usage": {"prompt_tokens": 15, "completion_tokens": 20, "total_tokens": 35}
            }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers,
                json=payload,
                timeout=60
            )
            if not response.ok:
                error_detail = response.text
                if self.is_production:
                    raise RuntimeError(f"OpenRouter API error {response.status_code}: {error_detail}")
                return {
                    "content": f"[API Error {response.status_code}] {error_detail}",
                    "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                }
                
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return {"content": content, "usage": usage}
        except requests.exceptions.Timeout:
            if self.is_production:
                raise RuntimeError(f"OpenRouter API timed out after 60 seconds for model {model}")
            return {
                "content": f"[Timeout] ไม่สามารถเชื่อมต่อ API ได้ในเวลาที่กำหนด",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }
        except Exception as e:
            if self.is_production:
                raise RuntimeError(f"OpenRouter API error: {str(e)}")
            return {
                "content": f"[API Error] {str(e)}",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }

    def _mock_response(self, message: str) -> Dict[str, Any]:
        """Mock fallback — ใช้เฉพาะ development เท่านั้น"""
        msg = message.lower()
        domain = "unknown"
        if "hello" in msg or "สวัสดี" in msg:
            domain = "smalltalk"
        elif "apple" in msg or "aapl" in msg:
            domain = "stock_quick_check"
        elif "rsi" in msg or "macd" in msg or "moving average" in msg:
            domain = "technical_analysis"

        mock_json = {
            "domain": domain,
            "sub_domains": ["test"],
            "ticker": "AAPL" if "aapl" in msg else None,
            "market": "US" if "aapl" in msg else None,
            "complexity": "low",
            "risk_profile_required": False,
            "needs_realtime_data": False,
            "selected_model_tier": "cheap",
            "reason": "[DEV MOCK] mock logic"
        }
        return {
            "parsed_json": mock_json,
            "raw_content": json.dumps(mock_json),
            "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20}
        }
