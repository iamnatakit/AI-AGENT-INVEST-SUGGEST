from project_2_investment_ai_agent_intent.app.router.token_policy import TokenPolicy
from project_2_investment_ai_agent_intent.app.llm_gateway.model_registry import ModelRegistry

class ModelRouter:
    def __init__(self):
        self.registry = ModelRegistry()
        
    def route_intent(self, intent_output: dict) -> dict:
        """
        Takes the parsed intent JSON and returns the routing decision.
        """
        domain = intent_output.get("domain", "unknown")
        complexity = intent_output.get("complexity", "medium")
        
        tier = TokenPolicy.get_tier_for_intent(domain, complexity)
        model = self.registry.get_model(tier)
        
        return {
            "selected_tier": tier,
            "selected_model": model,
            "action": "skip_llm" if tier == "none" else "call_llm"
        }
