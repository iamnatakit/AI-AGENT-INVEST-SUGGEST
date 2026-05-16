CREATE TABLE users (
    user_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255),
    risk_level VARCHAR(50),
    investment_horizon VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    user_id VARCHAR(100),
    project_name VARCHAR(100),
    session_summary TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_messages (
    message_id VARCHAR(100) PRIMARY KEY,
    session_id VARCHAR(100),
    user_id VARCHAR(100),
    project_name VARCHAR(100),
    role VARCHAR(50),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE intent_logs (
    intent_id VARCHAR(100) PRIMARY KEY,
    message_id VARCHAR(100),
    domain VARCHAR(100),
    sub_domains TEXT,
    selected_agent VARCHAR(100),
    selected_model_tier VARCHAR(50),
    selected_model VARCHAR(150),
    confidence_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usage_logs (
    usage_id VARCHAR(100) PRIMARY KEY,
    project_name VARCHAR(100),
    session_id VARCHAR(100),
    message_id VARCHAR(100),
    provider VARCHAR(100),
    model VARCHAR(150),
    domain VARCHAR(100),
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    reasoning_tokens INTEGER,
    cached_tokens INTEGER,
    total_tokens INTEGER,
    cost_usd FLOAT,
    latency_ms INTEGER,
    cache_hit BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE billing_ledger (
    billing_id VARCHAR(100) PRIMARY KEY,
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    message_id VARCHAR(100),
    project_name VARCHAR(100),
    model VARCHAR(150),
    total_tokens INTEGER,
    cost_usd FLOAT,
    cost_thb FLOAT,
    exchange_rate FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
