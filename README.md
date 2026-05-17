# AI Investment Chatbot Token Optimization Research

This repository contains the code and documentation for a comparative study between two AI agent architectures for investment advice. 

The goal is to empirically demonstrate that an optimized architecture leveraging an AI intent classifier, multi-agent frameworks, and dynamic model routing reduces token consumption, operational costs, and latency compared to a baseline system.

## Projects Overview

*   **Project 1: Investment AI Agent (Baseline)**
    *   A single large prompt chatbot.
    *   Uses a single LLM without intent routing.
    *   Serves as the control group for the study.

*   **Project 2: Investment AI Agent Intent (Optimized)**
    *   An optimized chatbot featuring an AI Intent Classifier.
    *   Leverages OpenRouter for LLM gateway routing and Google ADK for multi-agent orchestration.
    *   Includes token monitoring, cost monitoring, billing ledger, and chat history.

## Getting Started

### Running with Docker (Recommended)
The easiest way to run the complete system (both backends and the frontend UI) is using Docker Compose:

1. Ensure you have Docker and Docker Compose installed.
2. Configure your environment variables in `.env` (copy from `.env.example`).
3. Start the services:
   ```bash
   docker compose up --build -d
   ```
4. Access the web dashboard at: **http://localhost:3300**

To stop the services, run:
```bash
docker compose down
```

Check out the individual project directories and read the `PROJECT_BRIEF.md` for more details.
