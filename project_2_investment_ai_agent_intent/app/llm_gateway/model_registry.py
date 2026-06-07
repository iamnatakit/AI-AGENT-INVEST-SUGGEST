import os
from typing import Dict

class ModelRegistry:
    def __init__(self):
        # Allow overriding via environment variables (strip whitespace/CRLF)
        self.models = {
            "none": "none",
            "cheap": os.getenv("MODEL_CHEAP", "google/gemini-2.0-flash-001").strip(),
            "medium": os.getenv("MODEL_MEDIUM", "google/gemini-2.0-flash-001").strip(),
            "strong": os.getenv("MODEL_STRONG", "google/gemini-2.0-pro-exp-02-05").strip()
        }

    def get_model(self, tier: str) -> str:
        return self.models.get(tier, self.models["medium"])
