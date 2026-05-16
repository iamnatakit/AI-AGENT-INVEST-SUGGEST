from typing import Dict, Any
from shared.monitoring.cost_monitor import CostMonitor

class UsageParser:
    @staticmethod
    def parse_usage(openrouter_response: Dict[str, Any], model: str, latency_ms: int = 0) -> Dict[str, Any]:
        """
        Parses OpenRouter's usage block and tracks total cost.
        Uses OpenRouter's 'total_cost' if provided, otherwise falls back to estimated calculation.
        """
        usage_data = openrouter_response.get("usage", {})
        
        prompt_tokens = usage_data.get("prompt_tokens", 0)
        completion_tokens = usage_data.get("completion_tokens", 0)
        total_tokens = usage_data.get("total_tokens", prompt_tokens + completion_tokens)
        
        # Extended token fields sometimes provided by OpenRouter
        reasoning_tokens = usage_data.get("reasoning_tokens", 0)
        cached_tokens = usage_data.get("cached_tokens", 0)
        
        # Total cost provided by OpenRouter response root
        provided_cost = openrouter_response.get("total_cost")
        
        if provided_cost is not None:
            cost_usd = float(provided_cost)
        else:
            cost_usd = CostMonitor.calculate_cost_usd(model, prompt_tokens, completion_tokens)
            
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "reasoning_tokens": reasoning_tokens,
            "cached_tokens": cached_tokens,
            "total_tokens": total_tokens,
            "cost_usd": cost_usd,
            "latency_ms": latency_ms,
            "cache_hit": cached_tokens > 0
        }
