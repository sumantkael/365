from datetime import date
import unittest
from date_calculator import get_date_stats, parse_user_date

class TestDateCalculator(unittest.TestCase):
    def test_standard_non_leap_year(self):
        # 2023 was a non-leap year (365 days)
        d = date(2023, 1, 1)
        stats = get_date_stats(d)
        self.assertEqual(stats.year, 2023)
        self.assertEqual(stats.day_of_year, 1)
        self.assertFalse(stats.is_leap_year)
        self.assertEqual(stats.total_days, 365)
        self.assertEqual(stats.days_remaining, 364)

    def test_leap_year_february(self):
        # 2024 was a leap year (366 days)
        d = date(2024, 2, 29)
        stats = get_date_stats(d)
        self.assertEqual(stats.year, 2024)
        self.assertEqual(stats.day_of_year, 60) # 31 Jan + 29 Feb
        self.assertTrue(stats.is_leap_year)
        self.assertEqual(stats.total_days, 366)
        self.assertEqual(stats.days_remaining, 306)

    def test_leap_year_century_rules(self):
        # 2000 was a leap year (divisible by 400)
        stats_2000 = get_date_stats(date(2000, 12, 31))
        self.assertTrue(stats_2000.is_leap_year)
        self.assertEqual(stats_2000.total_days, 366)
        self.assertEqual(stats_2000.day_of_year, 366)
        self.assertEqual(stats_2000.days_remaining, 0)

        # 1900 was not a leap year (divisible by 100 but not 400)
        stats_1900 = get_date_stats(date(1900, 12, 31))
        self.assertFalse(stats_1900.is_leap_year)
        self.assertEqual(stats_1900.total_days, 365)
        self.assertEqual(stats_1900.day_of_year, 365)
        self.assertEqual(stats_1900.days_remaining, 0)

    def test_mid_year_date(self):
        # July 2 in a regular 365-day year
        d = date(2025, 7, 2)
        stats = get_date_stats(d)
        self.assertEqual(stats.day_of_year, 183)
        self.assertEqual(stats.days_remaining, 365 - 183)
        self.assertEqual(stats.percentage_elapsed, 50)
        self.assertEqual(stats.percentage_remaining, 50)

    def test_user_date_parsing(self):
        # Test specific user example: "21st of January 2027"
        dt1 = parse_user_date("21st of January 2027")
        self.assertEqual(dt1, date(2027, 1, 21))

        # Test other common variations
        self.assertEqual(parse_user_date("21st January 2027"), date(2027, 1, 21))
        self.assertEqual(parse_user_date("21 Jan 2027"), date(2027, 1, 21))
        self.assertEqual(parse_user_date("2027-01-21"), date(2027, 1, 21))
        self.assertEqual(parse_user_date("21/01/2027"), date(2027, 1, 21))
        self.assertEqual(parse_user_date("January 21, 2027"), date(2027, 1, 21))

    def test_custom_target_countdown(self):
        today = date(2026, 1, 1)
        target = date(2027, 1, 21)
        start = date(2025, 1, 1)

        stats = get_date_stats(
            target_date=today,
            date_mode="custom",
            custom_target_date=target,
            custom_start_date=start,
            event_title="Exam"
        )

        self.assertEqual(stats.days_remaining, (target - today).days)
        self.assertEqual(stats.total_days, (target - start).days)
        self.assertEqual(stats.event_title, "Exam")
        self.assertTrue(0 <= stats.percentage_elapsed <= 100)

    def test_custom_target_starting_today(self):
        # 1 month target starting today
        today = date(2026, 9, 24)
        target = date(2026, 10, 24)

        stats = get_date_stats(
            target_date=today,
            date_mode="custom",
            custom_target_date=target,
            custom_start_date=None,  # defaults to today
            event_title=""
        )

        self.assertEqual(stats.days_remaining, 30)
        self.assertEqual(stats.total_days, 30)
        self.assertEqual(stats.day_of_year, 1)  # Day 1 of 30
        self.assertEqual(stats.percentage_elapsed, 0)

    def test_custom_target_clamped_future_start(self):
        # If start date was accidentally set in future, clamp to today
        today = date(2026, 9, 24)
        target = date(2026, 10, 24)
        future_start = date(2026, 9, 28)

        stats = get_date_stats(
            target_date=today,
            date_mode="custom",
            custom_target_date=target,
            custom_start_date=future_start,
            event_title=""
        )

        self.assertEqual(stats.days_remaining, 30)
        self.assertEqual(stats.total_days, 30)
        self.assertEqual(stats.day_of_year, 1)

if __name__ == "__main__":
    unittest.main()
