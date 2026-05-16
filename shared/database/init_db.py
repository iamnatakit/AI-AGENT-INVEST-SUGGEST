from shared.database.db import engine, Base
# Ensure all models are imported before calling create_all
from shared.database.models import User, ChatSession, ChatMessage, IntentLog, UsageLog, BillingLedger

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database schema successfully initialized.")
