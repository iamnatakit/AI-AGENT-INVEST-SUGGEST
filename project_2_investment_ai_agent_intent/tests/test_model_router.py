import unittest
from project_2_investment_ai_agent_intent.app.router.model_router import ModelRouter
from project_2_investment_ai_agent_intent.app.llm_gateway.usage_parser import UsageParser

class TestModelRouter(unittest.TestCase):
    def setUp(self):
        self.router = ModelRouter()

    def test_smalltalk_routing(self):
        intent = {"domain": "smalltalk", "complexity": "low"}
        decision = self.router.route_intent(intent)
        self.assertEqual(decision["selected_tier"], "none")
        self.assertEqual(decision["action"], "skip_llm")

    def test_stock_quick_check_routing(self):
        # low complexity uses cheap
        intent = {"domain": "stock_quick_check", "complexity": "low"}
        decision = self.router.route_intent(intent)
        self.assertEqual(decision["selected_tier"], "cheap")
        
        # high complexity uses medium
        intent = {"domain": "stock_quick_check", "complexity": "high"}
        decision = self.router.route_intent(intent)
        self.assertEqual(decision["selected_tier"], "medium")

    def test_deep_analysis_routing(self):
        intent = {"domain": "stock_deep_analysis", "complexity": "high"}
        decision = self.router.route_intent(intent)
        self.assertEqual(decision["selected_tier"], "strong")
        self.assertEqual(decision["action"], "call_llm")

    def test_usage_parser_with_openrouter_cost(self):
        mock_response = {
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "reasoning_tokens": 10
            },
            "total_cost": 0.0052
        }
        usage = UsageParser.parse_usage(mock_response, "openai/gpt-4o", 250)
        self.assertEqual(usage["cost_usd"], 0.0052)
        self.assertEqual(usage["reasoning_tokens"], 10)
        self.assertEqual(usage["latency_ms"], 250)

    def test_usage_parser_fallback_cost(self):
        mock_response = {
            "usage": {
                "prompt_tokens": 1000000,
                "completion_tokens": 1000000
            }
        }
        # Expect fallback to cost monitor (1.25 + 5 = 6.25 for gemini-pro)
        usage = UsageParser.parse_usage(mock_response, "gemini-1.5-pro", 100)
        self.assertEqual(usage["cost_usd"], 6.25)
        self.assertEqual(usage["prompt_tokens"], 1000000)

if __name__ == '__main__':
    unittest.main()
