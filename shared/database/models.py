import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, Text, DateTime
from sqlalchemy.sql import func
from shared.database.db import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(String(100), primary_key=True, index=True)
    name = Column(String(255))
    risk_level = Column(String(50))
    investment_horizon = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    session_id = Column(String(100), primary_key=True, index=True)
    user_id = Column(String(100))
    project_name = Column(String(100))
    session_summary = Column(Text)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    message_id = Column(String(100), primary_key=True, index=True)
    session_id = Column(String(100))
    user_id = Column(String(100))
    project_name = Column(String(100))
    role = Column(String(50))
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class IntentLog(Base):
    __tablename__ = "intent_logs"
    intent_id = Column(String(100), primary_key=True, index=True)
    message_id = Column(String(100))
    domain = Column(String(100))
    sub_domains = Column(Text)
    selected_agent = Column(String(100))
    selected_model_tier = Column(String(50))
    selected_model = Column(String(150))
    confidence_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UsageLog(Base):
    __tablename__ = "usage_logs"
    usage_id = Column(String(100), primary_key=True, index=True)
    project_name = Column(String(100))
    session_id = Column(String(100))
    message_id = Column(String(100))
    provider = Column(String(100))
    model = Column(String(150))
    domain = Column(String(100), nullable=True)
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    reasoning_tokens = Column(Integer, default=0)
    cached_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer)
    cost_usd = Column(Float)
    latency_ms = Column(Integer)
    cache_hit = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class BillingLedger(Base):
    __tablename__ = "billing_ledger"
    billing_id = Column(String(100), primary_key=True, index=True)
    user_id = Column(String(100))
    session_id = Column(String(100))
    message_id = Column(String(100))
    project_name = Column(String(100))
    model = Column(String(150))
    total_tokens = Column(Integer)
    cost_usd = Column(Float)
    cost_thb = Column(Float)
    exchange_rate = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
