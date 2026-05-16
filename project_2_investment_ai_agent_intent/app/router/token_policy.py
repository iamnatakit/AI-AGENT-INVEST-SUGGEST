from typing import Dict

class TokenPolicy:
    # Mapping intent domains to recommended model tiers
    DOMAIN_TO_TIER: Dict[str, str] = {
        "smalltalk": "none",
        "general_finance": "cheap",
        "stock_quick_check": "medium",  # Can be dynamically downgraded based on complexity
        "technical_analysis": "medium",
        "fundamental_analysis": "strong",
        "stock_deep_analysis": "strong",
        "portfolio_analysis": "strong",
        "news_macro": "medium",
        "suitability": "medium",
        "compliance": "strong",
        "unknown": "medium"
    }

    @classmethod
    def get_tier_for_intent(cls, domain: str, complexity: str = "medium") -> str:
        base_tier = cls.DOMAIN_TO_TIER.get(domain, "medium")
        
        # Granular adjustment based on complexity
        if domain == "stock_quick_check":
            if complexity == "low":
                return "cheap"
            return "medium"
            
        return base_tier
