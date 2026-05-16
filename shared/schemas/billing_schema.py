from pydantic import BaseModel

class BillingLedgerCreate(BaseModel):
    billing_id: str
    user_id: str
    session_id: str
    message_id: str
    project_name: str
    model: str
    total_tokens: int
    cost_usd: float
    cost_thb: float
    exchange_rate: float
