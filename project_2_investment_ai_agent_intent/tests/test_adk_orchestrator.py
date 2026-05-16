import unittest
from project_2_investment_ai_agent_intent.app.adk_agents.orchestrator import AgentOrchestrator

class TestADKOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = AgentOrchestrator()

    def test_finance_education_route(self):
        intent = {"domain": "general_finance"}
        result = self.orchestrator.process("What is an ETF?", intent)
        self.assertEqual(result["selected_agent"], "FinanceEducationAgent")
        self.assertIn("DISCLAIMER:", result["final_response"])

    def test_market_snapshot_route(self):
        intent = {"domain": "stock_quick_check", "ticker": "TSLA"}
        result = self.orchestrator.process("Price of TSLA", intent)
        self.assertEqual(result["selected_agent"], "MarketSnapshotAgent")
        self.assertIn("TSLA", result["final_response"])

    def test_portfolio_risk_profile_check(self):
        intent = {"domain": "portfolio_analysis", "risk_profile_required": True}
        result = self.orchestrator.process("How is my portfolio?", intent, user_profile=None)
        self.assertEqual(result["agent_status"], "requires_action")
        self.assertIn("confirm your investment risk profile", result["final_response"])

    def test_portfolio_risk_profile_success(self):
        intent = {"domain": "portfolio_analysis", "risk_profile_required": True}
        user_profile = {"risk_level": "moderate"}
        result = self.orchestrator.process("How is my portfolio?", intent, user_profile=user_profile)
        self.assertEqual(result["agent_status"], "success")
        self.assertEqual(result["selected_agent"], "PortfolioRiskAgent")

    def test_compliance_violation_catch(self):
        from project_2_investment_ai_agent_intent.app.adk_agents.compliance_agent import ComplianceAgent
        comp = ComplianceAgent()
        res = comp.run("You should buy now to get rich!")
        self.assertEqual(res["status"], "violation_fixed")
        self.assertIn("[REDACTED FOR COMPLIANCE]", res["final_response"])
        self.assertIn("DISCLAIMER:", res["final_response"])

if __name__ == '__main__':
    unittest.main()
