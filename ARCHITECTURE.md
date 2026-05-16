# Architecture Overview

This research project consists of two distinct architectures for comparison.

## 1. Baseline Architecture (Project 1)
- **Frontend**: React-based UI for chat.
- **Backend**: FastAPI/Python backend.
- **LLM Integration**: Direct connection to a single LLM provider using one monolithic prompt.
- **Data**: Basic logging of chat, token, cost, and latency.

## 2. Optimized Architecture (Project 2)
- **Frontend**: Shared React-based UI.
- **Backend**: FastAPI/Python backend.
- **Routing Engine**: AI Intent Classifier determines the user's intent.
- **LLM Gateway**: OpenRouter to select the most cost-effective model based on intent.
- **Agent Framework**: Google ADK Agents handle specific domains (e.g., market data, portfolio analysis).
- **Data**: Comprehensive logging including a billing ledger and granular token/cost monitors.
