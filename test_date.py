from datetime import date
import unittest
from date_calculator import get_date_stats

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
        # Jan(31)+Feb(28)+Mar(31)+Apr(30)+May(31)+Jun(30)+2 = 183
        self.assertEqual(stats.day_of_year, 183)
        self.assertEqual(stats.days_remaining, 365 - 183)

if __name__ == "__main__":
    unittest.main()
