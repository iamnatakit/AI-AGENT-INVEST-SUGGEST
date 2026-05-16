from pydantic import BaseModel
from typing import Optional

class UsageLogCreate(BaseModel):
    usage_id: str
    project_name: str
    session_id: str
    message_id: str
    provider: str
    model: str
    domain: Optional[str] = None
    prompt_tokens: int
    completion_tokens: int
    reasoning_tokens: Optional[int] = 0
    cached_tokens: Optional[int] = 0
    total_tokens: int
    cost_usd: float
    latency_ms: int
    cache_hit: bool = False
