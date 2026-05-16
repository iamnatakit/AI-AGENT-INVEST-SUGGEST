from typing import Dict, Any

from .finance_education_agent import FinanceEducationAgent
from .market_snapshot_agent import MarketSnapshotAgent
from .technical_agent import TechnicalAgent
from .fundamental_agent import FundamentalAgent
from .portfolio_risk_agent import PortfolioRiskAgent
from .news_macro_agent import NewsMacroAgent
from .suitability_agent import SuitabilityAgent
from .compliance_agent import ComplianceAgent
from project_2_investment_ai_agent_intent.app.llm_gateway.openrouter_client import OpenRouterClient

class AgentOrchestrator:
    def __init__(self):
        self.agents = {
            "general_finance": FinanceEducationAgent(),
            "smalltalk": FinanceEducationAgent(), # Fallback for smalltalk
            "stock_quick_check": MarketSnapshotAgent(),
            "technical_analysis": TechnicalAgent(),
            "fundamental_analysis": FundamentalAgent(),
            "stock_deep_analysis": FundamentalAgent(), # Routes to deeper fundamental logic
            "portfolio_analysis": PortfolioRiskAgent(),
            "news_macro": NewsMacroAgent(),
            "suitability": SuitabilityAgent()
        }
        self.compliance_agent = ComplianceAgent()
        self.llm_client = OpenRouterClient()

    def process(self, user_message: str, intent_data: Dict[str, Any], user_profile: Dict[str, Any] = None, selected_model: str = "meta-llama/llama-3-8b-instruct:free") -> Dict[str, Any]:
        domain = intent_data.get("domain", "general_finance")
        ticker = intent_data.get("ticker")
        risk_profile_required = intent_data.get("risk_profile_required", False)
        
        agent = self.agents.get(domain, self.agents["general_finance"])
        
        # Pre-execution: Check user profile requirements
        risk_profile_present = user_profile is not None and "risk_level" in user_profile
        if risk_profile_required and not risk_profile_present:
             # Force safety prompt over normal generation
             draft = "Before I provide a personalized recommendation, please confirm your investment risk profile (e.g., conservative, moderate, aggressive)."
             agent_result = {"status": "requires_action"}
        else:
            # Execute primary agent to get draft logic
            agent_result = agent.run(
                user_message=user_message, 
                ticker=ticker, 
                risk_profile_present=risk_profile_present
            )
            
            # Fetch instructions from agent
            instructions = getattr(agent, "instructions", "You are a helpful investment AI assistant.")
            
            # Generate actual text using LLM Gateway
            llm_response = self.llm_client.generate_text_response(selected_model, instructions, user_message)
            draft = llm_response["content"]

        # Post-execution: Ensure all responses pass Compliance Checks
        compliance_result = self.compliance_agent.run(draft_response=draft)
        
        return {
            "selected_agent": agent.__class__.__name__,
            "agent_status": agent_result.get("status", "unknown"),
            "compliance_status": compliance_result.get("status"),
            "violations_found": compliance_result.get("violations", []),
            "final_response": compliance_result.get("final_response")
        }
