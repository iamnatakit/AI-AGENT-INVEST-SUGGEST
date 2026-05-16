import uuid
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from shared.database.db import get_db
from shared.database.models import ChatMessage, UsageLog
from shared.schemas.usage_schema import UsageLogCreate
from shared.schemas.billing_schema import BillingLedgerCreate
from shared.monitoring.token_monitor import TokenMonitor
from shared.monitoring.cost_monitor import CostMonitor
from shared.monitoring.latency_monitor import LatencyMonitor

from project_1_investment_ai_agent.app.llm.single_llm_client import SingleLLMClient
from project_1_investment_ai_agent.app.prompts.big_investment_prompt import BIG_INVESTMENT_PROMPT

router = APIRouter()
llm_client = SingleLLMClient()

class ChatRequest(BaseModel):
    session_id: str
    user_id: str
    message: str

class ChatResponse(BaseModel):
    message: str
    usage: Dict[str, Any]
    cost_usd: float
    latency_ms: int

@LatencyMonitor.measure_latency_async
async def process_chat(request: ChatRequest, db: Optional[Session]) -> Dict[str, Any]:
    # 1. Save User Message (non-fatal)
    user_msg_id = str(uuid.uuid4())
    if db:
        try:
            db_user_msg = ChatMessage(
                message_id=user_msg_id,
                session_id=request.session_id,
                user_id=request.user_id,
                project_name="project_1_baseline",
                role="user",
                content=request.message
            )
            db.add(db_user_msg)
            db.flush()
        except Exception as e:
            print(f"⚠️ DB write user msg skipped: {e}")

    # 2. Call LLM
    llm_response = llm_client.generate_response(BIG_INVESTMENT_PROMPT, request.message)
    content = llm_response["content"]
    usage = llm_response["usage"]
    model = llm_response["model"]

    # 3. Save Assistant Message (non-fatal)
    assistant_msg_id = str(uuid.uuid4())
    usage_log_id = str(uuid.uuid4())
    if db:
        try:
            db_assistant_msg = ChatMessage(
                message_id=assistant_msg_id,
                session_id=request.session_id,
                user_id=request.user_id,
                project_name="project_1_baseline",
                role="assistant",
                content=content
            )
            db.add(db_assistant_msg)
            db.commit()
        except Exception as e:
            print(f"⚠️ DB write assistant msg skipped: {e}")
            try: db.rollback()
            except: pass

    # 4. Calculate Cost
    cost_usd = CostMonitor.calculate_cost_usd(
        model=model,
        prompt_tokens=usage["prompt_tokens"],
        completion_tokens=usage["completion_tokens"]
    )
    cost_thb = CostMonitor.convert_usd_to_thb(cost_usd)

    # 5. Save Usage Log (non-fatal)
    if db:
        try:
            usage_data = UsageLogCreate(
                usage_id=usage_log_id,
                project_name="project_1_baseline",
                session_id=request.session_id,
                message_id=assistant_msg_id,
                provider="openrouter",
                model=model,
                domain="investment",
                prompt_tokens=usage["prompt_tokens"],
                completion_tokens=usage["completion_tokens"],
                total_tokens=usage["total_tokens"],
                cost_usd=cost_usd,
                latency_ms=0,
                cache_hit=False
            )
            TokenMonitor.save_usage_log(db, usage_data)
        except Exception as e:
            print(f"⚠️ DB write usage log skipped: {e}")

        # 6. Save Billing Ledger (non-fatal)
        try:
            billing_data = BillingLedgerCreate(
                billing_id=str(uuid.uuid4()),
                user_id=request.user_id,
                session_id=request.session_id,
                message_id=assistant_msg_id,
                project_name="project_1_baseline",
                model=model,
                total_tokens=usage["total_tokens"],
                cost_usd=cost_usd,
                cost_thb=cost_thb,
                exchange_rate=36.5
            )
            CostMonitor.save_billing_record(db, billing_data)
        except Exception as e:
            print(f"⚠️ DB write billing skipped: {e}")

    return {
        "message": content,
        "usage": usage,
        "cost_usd": cost_usd,
        "usage_log_id": usage_log_id
    }

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        result, latency_ms = await process_chat(request, db)

        # Update latency (non-fatal)
        if db:
            try:
                db_usage = db.query(UsageLog).filter(UsageLog.usage_id == result["usage_log_id"]).first()
                if db_usage:
                    db_usage.latency_ms = latency_ms
                    db.commit()
            except Exception:
                pass

        return ChatResponse(
            message=result["message"],
            usage=result["usage"],
            cost_usd=result["cost_usd"],
            latency_ms=latency_ms
        )
    except Exception as e:
        return JSONResponse(
            status_code=200,
            content={
                "message": f"⚠️ เกิดข้อผิดพลาด: {str(e)}",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "cost_usd": 0.0,
                "latency_ms": 0
            }
        )
