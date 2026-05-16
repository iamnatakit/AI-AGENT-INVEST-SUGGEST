import unittest
from shared.monitoring.cost_monitor import CostMonitor

class TestCostMonitor(unittest.TestCase):
    def test_calculate_cost_usd_gemini_pro(self):
        cost = CostMonitor.calculate_cost_usd("gemini-1.5-pro", 1_000_000, 1_000_000)
        self.assertEqual(cost, 6.25)

    def test_calculate_cost_usd_gpt_4o(self):
        cost = CostMonitor.calculate_cost_usd("gpt-4o", 2_000_000, 500_000)
        self.assertEqual(cost, 17.50)

    def test_calculate_cost_usd_unknown_model(self):
        cost = CostMonitor.calculate_cost_usd("unknown-model", 1000, 1000)
        self.assertEqual(cost, 0.0)

    def test_convert_usd_to_thb(self):
        thb = CostMonitor.convert_usd_to_thb(10.0, 36.0)
        self.assertEqual(thb, 360.0)

if __name__ == '__main__':
    unittest.main()
