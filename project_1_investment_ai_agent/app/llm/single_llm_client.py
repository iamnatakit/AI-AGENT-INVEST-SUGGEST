import os
import requests
from typing import Dict, Any

class SingleLLMClient:
    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1"

    @property
    def model(self):
        return os.getenv("BASELINE_MODEL", "google/gemini-2.0-flash-001")

    @property
    def api_key(self):
        return os.getenv("OPENROUTER_API_KEY", "")

    @property
    def is_production(self):
        return os.getenv("ENVIRONMENT", "development") == "production"

    def generate_response(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        if not self.api_key:
            if self.is_production:
                raise RuntimeError("OPENROUTER_API_KEY is not set. Cannot run in production without a valid API key.")
            return self._mock_response(system_prompt, user_message)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://investment-ai-agent.local",
            "X-Title": "Investment AI Agent (Baseline)"
        }
        payload = {
            "model": self.model,
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
                headers=headers,
                json=payload,
                timeout=60
            )
            if not response.ok:
                error_detail = response.text
                if self.is_production:
                    raise RuntimeError(f"OpenRouter API error {response.status_code}: {error_detail}")
                return self._mock_response(system_prompt, f"{user_message} (API Error {response.status_code}: {error_detail})")
            
            data = response.json()

            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return {
                "content": content,
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                },
                "model": self.model
            }
        except requests.exceptions.Timeout:
            if self.is_production:
                raise RuntimeError(f"OpenRouter API timed out after 60 seconds for model {self.model}")
            return self._mock_response(system_prompt, f"{user_message} (Timeout)")
        except Exception as e:
            if self.is_production:
                raise RuntimeError(f"OpenRouter API error: {str(e)}")
            return self._mock_response(system_prompt, f"{user_message} (API Error: {str(e)})")

    def _mock_response(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        """Mock fallback — ใช้เฉพาะ development เท่านั้น"""
        content = (
            f"[DEV MOCK] ได้รับคำถาม: '{user_message}' — "
            "กรุณาตั้งค่า OPENROUTER_API_KEY และ ENVIRONMENT=production เพื่อใช้ AI จริง\n\n"
            "⚠️ คำเตือน: การลงทุนมีความเสี่ยง ผู้ลงทุนอาจได้รับเงินคืนน้อยกว่าเงินลงทุนเริ่มต้น "
            "ข้อมูลนี้จัดทำขึ้นเพื่อการศึกษาเท่านั้น ไม่ถือเป็นคำแนะนำทางการเงิน"
        )
        prompt_tokens = len(system_prompt.split()) + len(user_message.split())
        completion_tokens = len(content.split())
        return {
            "content": content,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            },
            "model": self.model
        }
