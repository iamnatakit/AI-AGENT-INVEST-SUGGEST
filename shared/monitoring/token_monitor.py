from sqlalchemy.orm import Session
from shared.database.models import UsageLog
from shared.schemas.usage_schema import UsageLogCreate

class TokenMonitor:
    @staticmethod
    def save_usage_log(db: Session, usage_data: UsageLogCreate) -> UsageLog:
        # Convert pydantic model to dict, compatible with SQLAlchemy kwargs
        db_usage = UsageLog(**usage_data.model_dump() if hasattr(usage_data, "model_dump") else usage_data.dict())
        db.add(db_usage)
        db.commit()
        db.refresh(db_usage)
        return db_usage
