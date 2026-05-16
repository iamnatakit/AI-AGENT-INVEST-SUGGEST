from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from project_1_investment_ai_agent.app.routes import chat

load_dotenv(override=True)

app = FastAPI(title="Investment AI Agent (Baseline)")

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

app.include_router(chat.router, prefix="/investment-ai-agent")

@app.get("/health")
def health_check():
    return {"status": "ok", "project": "project_1"}
