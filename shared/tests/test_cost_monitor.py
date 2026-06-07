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
        # Unknown models should fallback to standard cheap rate: prompt 0.075, completion 0.30
        cost = CostMonitor.calculate_cost_usd("unknown-model", 1_000_000, 1_000_000)
        self.assertEqual(cost, 0.375)

    def test_calculate_cost_usd_free_model(self):
        # Models containing 'free' should be costed at 0.0
        cost = CostMonitor.calculate_cost_usd("google/gemini-3.1-flash:free", 1_000_000, 1_000_000)
        self.assertEqual(cost, 0.0)

    def test_calculate_cost_usd_none_model(self):
        # Model 'none' should be costed at 0.0
        cost = CostMonitor.calculate_cost_usd("none", 1_000_000, 1_000_000)
        self.assertEqual(cost, 0.0)

    def test_calculate_cost_usd_gemini_3_1_flash_lite(self):
        # Google Gemini 3.1 Flash-Lite: prompt 0.25, completion 1.50
        cost = CostMonitor.calculate_cost_usd("google/gemini-3.1-flash-lite", 2_000_000, 500_000)
        self.assertEqual(cost, 1.25) # (2 * 0.25) + (0.5 * 1.5) = 0.5 + 0.75 = 1.25

    def test_calculate_cost_usd_gemini_3_1_pro_preview(self):
        # Google Gemini 3.1 Pro Preview: prompt 2.00, completion 12.00
        cost = CostMonitor.calculate_cost_usd("google/gemini-3.1-pro-preview", 1_000_000, 1_000_000)
        self.assertEqual(cost, 14.00)

    def test_calculate_cost_usd_fuzzy_match(self):
        # Fuzzy match for a variant of gpt-4o (e.g. gpt-4o-2024-05-13)
        cost = CostMonitor.calculate_cost_usd("gpt-4o-2024-05-13", 1_000_000, 1_000_000)
        self.assertEqual(cost, 20.00) # prompt 5.00 + completion 15.00 = 20.00

    def test_convert_usd_to_thb(self):
        thb = CostMonitor.convert_usd_to_thb(10.0, 36.0)
        self.assertEqual(thb, 360.0)

if __name__ == '__main__':
    unittest.main()
