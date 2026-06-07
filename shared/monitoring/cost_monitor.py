from sqlalchemy.orm import Session
from shared.database.models import BillingLedger
from shared.schemas.billing_schema import BillingLedgerCreate

# Standard per 1M tokens pricing (OpenRouter rates as of 2025/2026)
MODEL_PRICING = {
    # Google Gemini
    "gemini-1.5-pro": {"prompt": 1.25, "completion": 5.00},
    "gemini-1.5-flash": {"prompt": 0.075, "completion": 0.30},
    "google/gemini-1.5-pro": {"prompt": 1.25, "completion": 5.00},
    "google/gemini-1.5-flash": {"prompt": 0.075, "completion": 0.30},
    "google/gemini-1.5-flash-8b": {"prompt": 0.0375, "completion": 0.15},
    "google/gemini-2.0-flash-001": {"prompt": 0.10, "completion": 0.40},
    "google/gemini-2.0-pro-exp-02-05": {"prompt": 1.25, "completion": 5.00},
    "google/gemini-3.1-flash-lite": {"prompt": 0.25, "completion": 1.50},
    "google/gemini-3.1-pro-preview": {"prompt": 2.00, "completion": 12.00},
    "google/gemini-3.1-pro-preview-customtools": {"prompt": 2.00, "completion": 12.00},
    # OpenAI
    "gpt-4o": {"prompt": 5.00, "completion": 15.00},
    "gpt-3.5-turbo": {"prompt": 0.50, "completion": 1.50},
    # Meta LLaMA (free tier via OpenRouter)
    "meta-llama/llama-3-8b-instruct:free": {"prompt": 0.0, "completion": 0.0},
    "meta-llama/llama-3-8b-instruct": {"prompt": 0.055, "completion": 0.055},
    "meta-llama/llama-3-70b-instruct": {"prompt": 0.59, "completion": 0.79},
    "meta-llama/llama-3.1-8b-instruct:free": {"prompt": 0.0, "completion": 0.0},
    "meta-llama/llama-3.1-70b-instruct": {"prompt": 0.52, "completion": 0.75},
}

class CostMonitor:
    @staticmethod
    def calculate_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
        if not model:
            return 0.0
            
        model_lower = model.lower()
        if "free" in model_lower or model_lower == "none":
            return 0.0

        # Try exact match first
        pricing = MODEL_PRICING.get(model)
        if not pricing:
            # Try fuzzy substring match
            for key, val in MODEL_PRICING.items():
                if key in model or model in key:
                    pricing = val
                    break

        if not pricing:
            # Fallback to standard cheap rate if unknown and not free
            pricing = {"prompt": 0.075, "completion": 0.30}

        prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]
        return prompt_cost + completion_cost

    @staticmethod
    def convert_usd_to_thb(usd_amount: float, exchange_rate: float = 36.5) -> float:
        return usd_amount * exchange_rate

    @staticmethod
    def save_billing_record(db: Session, record: BillingLedgerCreate) -> BillingLedger:
        db_billing = BillingLedger(**record.model_dump() if hasattr(record, "model_dump") else record.dict())
        db.add(db_billing)
        db.commit()
        db.refresh(db_billing)
        return db_billing
