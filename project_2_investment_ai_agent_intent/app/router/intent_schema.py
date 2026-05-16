from pydantic import BaseModel, Field
from typing import List, Optional

class IntentOutput(BaseModel):
    domain: str = Field(..., description="The main intent domain")
    sub_domains: List[str] = Field(default_factory=list)
    ticker: Optional[str] = Field(None)
    market: Optional[str] = Field(None)
    complexity: str = Field(..., description="low, medium, or high")
    risk_profile_required: bool = Field(...)
    needs_realtime_data: bool = Field(...)
    selected_model_tier: str = Field(..., description="cheap, medium, or strong")
    reason: str = Field(...)

# JSON schema สำหรับ OpenRouter models ที่รองรับ json_object เท่านั้น
INTENT_JSON_INSTRUCTION = """
ตอบกลับด้วย JSON object เท่านั้น ไม่มีข้อความอื่น ตาม format ต่อไปนี้:
{
  "domain": "<หนึ่งใน: smalltalk, general_finance, stock_quick_check, technical_analysis, fundamental_analysis, stock_deep_analysis, portfolio_analysis, news_macro, suitability, compliance, unknown>",
  "sub_domains": ["<หัวข้อย่อย>"],
  "ticker": "<ชื่อหุ้น หรือ null>",
  "market": "<US, TH, หรือ null>",
  "complexity": "<low, medium, หรือ high>",
  "risk_profile_required": <true หรือ false>,
  "needs_realtime_data": <true หรือ false>,
  "selected_model_tier": "<cheap, medium, หรือ strong>",
  "reason": "<เหตุผลสั้นๆ>"
}
"""

def get_intent_json_schema():
    """ส่งคืน None เพราะใช้ json_object แทน json_schema"""
    return None
