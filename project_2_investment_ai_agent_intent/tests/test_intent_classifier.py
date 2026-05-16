import os
import unittest
from project_2_investment_ai_agent_intent.app.router.intent_classifier import IntentClassifier
from project_2_investment_ai_agent_intent.app.llm_gateway.openrouter_client import OpenRouterClient

class MockOpenRouterClient(OpenRouterClient):
    def generate_structured_response(self, model, system_prompt, user_message, json_schema):
        msg = user_message.lower()
        
        # Test Case handling logic
        if "invalid_json_trigger" in msg:
            return {"parsed_json": None, "raw_content": "{bad json}", "usage": {}}
        elif "validation_fail_trigger" in msg:
            # Return JSON that breaks validation schema (missing required field)
            return {"parsed_json": {"domain": "smalltalk"}, "raw_content": "{}", "usage": {}}
        elif "hello" in msg:
            domain = "smalltalk"
        elif "aapl" in msg or "stock" in msg:
            domain = "stock_quick_check"
        elif "pe ratio" in msg:
            domain = "fundamental_analysis"
        elif "rsi" in msg:
            domain = "technical_analysis"
        elif "portfolio" in msg:
            domain = "portfolio_analysis"
        elif "fed rate" in msg:
            domain = "news_macro"
        elif "am i ready" in msg:
            domain = "suitability"
        elif "legal rules" in msg:
            domain = "compliance"
        else:
            domain = "unknown"
            
        return {
            "parsed_json": {
                "domain": domain,
                "sub_domains": [],
                "ticker": "AAPL" if "aapl" in msg else None,
                "market": None,
                "complexity": "low",
                "risk_profile_required": False,
                "needs_realtime_data": False,
                "selected_model_tier": "fast",
                "reason": "mock"
            },
            "raw_content": "",
            "usage": {"total_tokens": 10}
        }

class TestIntentClassifier(unittest.TestCase):
    def setUp(self):
        self.mock_client = MockOpenRouterClient()
        self.classifier = IntentClassifier(client=self.mock_client)

    def test_smalltalk_intent(self):
        res = self.classifier.classify("hello there")
        self.assertEqual(res["intent"]["domain"], "smalltalk")

    def test_stock_quick_check_intent(self):
        res = self.classifier.classify("what is the price of AAPL?")
        self.assertEqual(res["intent"]["domain"], "stock_quick_check")

    def test_fundamental_analysis_intent(self):
        res = self.classifier.classify("what is the PE ratio of this company?")
        self.assertEqual(res["intent"]["domain"], "fundamental_analysis")

    def test_technical_analysis_intent(self):
        res = self.classifier.classify("is the RSI overbought?")
        self.assertEqual(res["intent"]["domain"], "technical_analysis")

    def test_portfolio_analysis_intent(self):
        res = self.classifier.classify("review my portfolio allocation")
        self.assertEqual(res["intent"]["domain"], "portfolio_analysis")

    def test_news_macro_intent(self):
        res = self.classifier.classify("will the fed rate cut happen soon?")
        self.assertEqual(res["intent"]["domain"], "news_macro")

    def test_suitability_intent(self):
        res = self.classifier.classify("am i ready to invest in crypto?")
        self.assertEqual(res["intent"]["domain"], "suitability")

    def test_compliance_intent(self):
        res = self.classifier.classify("what are the legal rules for trading?")
        self.assertEqual(res["intent"]["domain"], "compliance")

    def test_unknown_intent(self):
        res = self.classifier.classify("xyz123")
        self.assertEqual(res["intent"]["domain"], "unknown")

    def test_invalid_json_handling(self):
        res = self.classifier.classify("invalid_json_trigger")
        self.assertEqual(res["intent"]["domain"], "unknown")
        self.assertEqual(res["intent"]["reason"], "Failed to parse JSON or API error")
        
    def test_validation_schema_handling(self):
        res = self.classifier.classify("validation_fail_trigger")
        self.assertEqual(res["intent"]["domain"], "unknown")
        self.assertTrue("Validation failed" in res["intent"]["reason"])

if __name__ == '__main__':
    unittest.main()
