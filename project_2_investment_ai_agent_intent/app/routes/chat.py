import uuid
import json
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from shared.database.db import get_db
from shared.database.models import ChatMessage, IntentLog, UsageLog, BillingLedger, User
from shared.schemas.usage_schema import UsageLogCreate
from shared.schemas.billing_schema import BillingLedgerCreate
from shared.monitoring.token_monitor import TokenMonitor
from shared.monitoring.cost_monitor import CostMonitor
from shared.monitoring.latency_monitor import LatencyMonitor

from project_2_investment_ai_agent_intent.app.router.intent_classifier import IntentClassifier
from project_2_investment_ai_agent_intent.app.router.model_router import ModelRouter
from project_2_investment_ai_agent_intent.app.adk_agents.orchestrator import AgentOrchestrator
from project_2_investment_ai_agent_intent.app.llm_gateway.usage_parser import UsageParser

router = APIRouter()
intent_classifier = IntentClassifier()
model_router = ModelRouter()
adk_orchestrator = AgentOrchestrator()

class ChatRequest(BaseModel):
    session_id: str
    user_id: str
    message: str

class ChatResponse(BaseModel):
    answer: str
    intent: Dict[str, Any]
    selected_agent: str
    selected_model: str
    usage: Dict[str, Any]
    billing: Dict[str, Any]
    latency_ms: int

@LatencyMonitor.measure_latency_async
async def process_optimized_chat(request: ChatRequest, db: Optional[Session]) -> Dict[str, Any]:
    # 1. Fetch user profile (non-fatal)
    user_profile = None
    if db:
        try:
            db_user = db.query(User).filter(User.user_id == request.user_id).first()
            if db_user:
                user_profile = {"risk_level": db_user.risk_level}
        except Exception as e:
            print(f"⚠️ DB fetch user skipped: {e}")

    # 2. Save User Message (non-fatal)
    user_msg_id = str(uuid.uuid4())
    if db:
        try:
            db_user_msg = ChatMessage(
                message_id=user_msg_id,
                session_id=request.session_id,
                user_id=request.user_id,
                project_name="project_2_intent",
                role="user",
                content=request.message
            )
            db.add(db_user_msg)
            db.flush()
        except Exception as e:
            print(f"⚠️ DB write user msg skipped: {e}")

    # 3. Intent Classification
    intent_result = intent_classifier.classify(request.message)
    intent_data = intent_result["intent"]

    # 4. Model Routing
    routing_decision = model_router.route_intent(intent_data)
    selected_model = routing_decision["selected_model"]

    # 5. ADK Orchestrator
    adk_result = adk_orchestrator.process(
        user_message=request.message,
        intent_data=intent_data,
        user_profile=user_profile,
        selected_model=selected_model
    )
    final_response = adk_result["final_response"]
    selected_agent = adk_result["selected_agent"]

    # 6. Save Assistant Message (non-fatal)
    assistant_msg_id = str(uuid.uuid4())
    if db:
        try:
            db_assistant_msg = ChatMessage(
                message_id=assistant_msg_id,
                session_id=request.session_id,
                user_id=request.user_id,
                project_name="project_2_intent",
                role="assistant",
                content=final_response
            )
            db.add(db_assistant_msg)
        except Exception as e:
            print(f"⚠️ DB write assistant msg skipped: {e}")

    # 7. Save Intent Log (non-fatal)
    if db:
        try:
            db_intent_log = IntentLog(
                intent_id=str(uuid.uuid4()),
                message_id=user_msg_id,
                domain=intent_data.get("domain", "unknown"),
                sub_domains=json.dumps(intent_data.get("sub_domains", [])),
                selected_agent=selected_agent,
                selected_model_tier=routing_decision["selected_tier"],
                selected_model=selected_model,
                confidence_score=0.95
            )
            db.add(db_intent_log)
            db.commit()
        except Exception as e:
            print(f"⚠️ DB write intent log skipped: {e}")
            try: db.rollback()
            except: pass

    # 8. Usage Parsing
    combined_usage_raw = {
        "usage": {
            "prompt_tokens": intent_result.get("usage", {}).get("prompt_tokens", 15) + 50,
            "completion_tokens": intent_result.get("usage", {}).get("completion_tokens", 20) + len(final_response.split())
        }
    }
    parsed_usage = UsageParser.parse_usage(combined_usage_raw, selected_model, latency_ms=0)

    # 9. Save Usage Log (non-fatal)
    usage_log_id = str(uuid.uuid4())
    if db:
        try:
            usage_data_create = UsageLogCreate(
                usage_id=usage_log_id,
                project_name="project_2_intent",
                session_id=request.session_id,
                message_id=assistant_msg_id,
                provider="openrouter",
                model=selected_model,
                domain=intent_data.get("domain", "unknown"),
                prompt_tokens=parsed_usage["prompt_tokens"],
                completion_tokens=parsed_usage["completion_tokens"],
                total_tokens=parsed_usage["total_tokens"],
                cost_usd=parsed_usage["cost_usd"],
                latency_ms=0,
                cache_hit=parsed_usage["cache_hit"]
            )
            TokenMonitor.save_usage_log(db, usage_data_create)
        except Exception as e:
            print(f"⚠️ DB write usage log skipped: {e}")

    # 10. Save Billing Ledger (non-fatal)
    cost_thb = CostMonitor.convert_usd_to_thb(parsed_usage["cost_usd"])
    if db:
        try:
            billing_data = BillingLedgerCreate(
                billing_id=str(uuid.uuid4()),
                user_id=request.user_id,
                session_id=request.session_id,
                message_id=assistant_msg_id,
                project_name="project_2_intent",
                model=selected_model,
                total_tokens=parsed_usage["total_tokens"],
                cost_usd=parsed_usage["cost_usd"],
                cost_thb=cost_thb,
                exchange_rate=36.5
            )
            CostMonitor.save_billing_record(db, billing_data)
        except Exception as e:
            print(f"⚠️ DB write billing skipped: {e}")

    return {
        "answer": final_response,
        "intent": intent_data,
        "selected_agent": selected_agent,
        "selected_model": selected_model,
        "usage": parsed_usage,
        "billing": {
            "cost_usd": parsed_usage["cost_usd"],
            "cost_thb": cost_thb
        },
        "usage_log_id": usage_log_id
    }

@router.post("/chat", response_model=ChatResponse)
async def optimized_chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        result, latency_ms = await process_optimized_chat(request, db)

        # Update latency (non-fatal)
        if db:
            try:
                usage_log_id = result.get("usage_log_id")
                db_usage = db.query(UsageLog).filter(UsageLog.usage_id == usage_log_id).first()
                if db_usage:
                    db_usage.latency_ms = latency_ms
                    db.commit()
            except Exception:
                pass

        result.pop("usage_log_id", None)
        result["latency_ms"] = latency_ms
        result["usage"]["latency_ms"] = latency_ms

        return ChatResponse(**result)
    except Exception as e:
        return JSONResponse(
            status_code=200,
            content={
                "answer": f"⚠️ เกิดข้อผิดพลาด: {str(e)}",
                "intent": {"domain": "unknown"},
                "selected_agent": "ErrorHandler",
                "selected_model": "none",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "latency_ms": 0},
                "billing": {"cost_usd": 0.0, "cost_thb": 0.0},
                "latency_ms": 0
            }
        )
