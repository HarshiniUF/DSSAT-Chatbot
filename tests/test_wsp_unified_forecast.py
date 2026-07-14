import unittest
from datetime import date
from unittest.mock import Mock

from wsp_unified_forecast import (
    analyse_rain,
    build_forecast_context,
    fetch_daily_forecast,
    format_forecast_for_prompt,
    is_forecast_relevant,
)


class UnifiedForecastTests(unittest.TestCase):
    def test_forecast_relevance_is_selective(self):
        self.assertTrue(is_forecast_relevant("Is it safe to spray fungicide this week?"))
        self.assertTrue(is_forecast_relevant("Will it rain tomorrow?"))
        self.assertFalse(is_forecast_relevant("Why is nitrogen important for maize?"))

    def test_analyse_rain_uses_normalized_daily_records(self):
        forecast = {
            "daily": [
                {"date": "2026-07-14", "precipitation_mm": 0.2},
                {"date": "2026-07-15", "precipitation_mm": 4.5},
                {"date": "2026-07-16", "precipitation_mm": 2.0},
            ]
        }
        result = analyse_rain(forecast)
        self.assertEqual(result["num_rainy_days"], 2)
        self.assertEqual(result["next_rainy_day"], "2026-07-15")
        self.assertEqual(result["peak_rain_mm"], 4.5)
        self.assertEqual(result["total_forecast_rain_mm"], 6.7)

    def test_daily_provider_is_normalized(self):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "latitude": 1.0,
            "longitude": 35.0,
            "timezone": "Africa/Nairobi",
            "daily": {
                "time": ["2026-07-14"],
                "precipitation_sum": [3.25],
                "precipitation_probability_max": [70],
                "temperature_2m_max": [24.0],
                "temperature_2m_min": [13.0],
            },
        }
        request_get = Mock(return_value=response)
        result = fetch_daily_forecast(1.0, 35.0, request_get=request_get)
        self.assertEqual(result["daily"][0]["precipitation_mm"], 3.25)
        self.assertEqual(result["daily"][0]["precipitation_probability_pct"], 70.0)
        request_get.assert_called_once()

    def test_irrelevant_question_does_not_call_providers(self):
        daily = Mock()
        seasonal = Mock()
        result = build_forecast_context(
            "What is DSSAT?",
            {"region": "Kitale, Kenya"},
            1.0,
            35.0,
            today=date(2026, 7, 14),
            daily_fetcher=daily,
            seasonal_fetcher=seasonal,
        )
        self.assertEqual(result["status"], "not_relevant")
        daily.assert_not_called()
        seasonal.assert_not_called()

    def test_one_provider_failure_does_not_discard_other_context(self):
        daily_result = {
            "provider": "daily-test",
            "fetched_start_date": "2026-07-14",
            "fetched_end_date": "2026-07-15",
            "daily": [{"date": "2026-07-14", "precipitation_mm": 2.0}],
        }
        result = build_forecast_context(
            "Should I spray this week?",
            {"region": "Kitale, Kenya"},
            1.0,
            35.0,
            today=date(2026, 7, 14),
            daily_fetcher=Mock(return_value=daily_result),
            seasonal_fetcher=Mock(side_effect=RuntimeError("seasonal offline")),
        )
        self.assertEqual(result["status"], "available")
        self.assertEqual(result["daily_analysis"]["next_rainy_day"], "2026-07-14")
        self.assertIn("seasonal forecast unavailable", result["errors"][0])
        prompt_context = format_forecast_for_prompt(result)
        self.assertIn("daily-test", prompt_context)
        self.assertIn("seasonal offline", prompt_context)


if __name__ == "__main__":
    unittest.main()
