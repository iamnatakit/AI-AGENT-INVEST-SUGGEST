from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from project_2_investment_ai_agent_intent.app.routes import chat, history

load_dotenv(override=True)

app = FastAPI(title="Investment AI Agent Intent (Optimized)", debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    try:
        from shared.database.init_db import init_db
        init_db()
        print("✅ Database tables created/verified.")
    except Exception as e:
        print(f"⚠️  DB init warning (non-fatal): {e}")

app.include_router(chat.router, prefix="/investment-ai-agent-intent")
app.include_router(history.router, prefix="/investment-ai-agent-intent")

from fastapi import Request
from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "traceback": traceback.format_exc()}
    )

@app.get("/health")
def health_check():
    # Force reload
    return {"status": "ok", "project": "project_2_intent"}
