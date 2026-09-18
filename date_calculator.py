from datetime import date
import calendar

class DateStats:
    def __init__(self, target_date: date = None):
        self.date = target_date or date.today()
        self.year = self.date.year
        self.day_of_year = self.date.timetuple().tm_yday
        self.is_leap_year = calendar.isleap(self.year)
        self.total_days = 366 if self.is_leap_year else 365
        self.days_remaining = self.total_days - self.day_of_year
        self.percentage_elapsed_exact = (self.day_of_year / self.total_days) * 100
        self.percentage_elapsed = round(self.percentage_elapsed_exact)
        self.percentage_remaining_exact = 100 - self.percentage_elapsed_exact
        self.percentage_remaining = round(self.percentage_remaining_exact)

    def to_dict(self):
        return {
            "year": self.year,
            "day_of_year": self.day_of_year,
            "is_leap_year": self.is_leap_year,
            "total_days": self.total_days,
            "days_remaining": self.days_remaining,
            "percentage_elapsed": self.percentage_elapsed,
            "percentage_remaining": self.percentage_remaining,
        }

    def __repr__(self):
        return (
            f"<DateStats year={self.year} day={self.day_of_year}/{self.total_days} "
            f"({self.percentage_elapsed}%) remaining={self.days_remaining} leap={self.is_leap_year}>"
        )


def get_date_stats(target_date: date = None) -> DateStats:
    """Returns calculated day stats for target_date or today."""
    return DateStats(target_date)
