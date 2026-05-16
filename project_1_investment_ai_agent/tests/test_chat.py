import unittest
from project_1_investment_ai_agent.app.llm.single_llm_client import SingleLLMClient
from project_1_investment_ai_agent.app.prompts.big_investment_prompt import BIG_INVESTMENT_PROMPT

class TestProject1Chat(unittest.TestCase):
    def test_llm_client_returns_disclaimer(self):
        client = SingleLLMClient()
        response = client.generate_response(BIG_INVESTMENT_PROMPT, "Should I buy stocks?")
        
        self.assertIn("DISCLAIMER:", response["content"])
        self.assertIn("usage", response)
        self.assertGreater(response["usage"]["total_tokens"], 0)
        self.assertIn("model", response)

if __name__ == '__main__':
    unittest.main()
