from datetime import date, datetime
import calendar
import re

class DateStats:
    def __init__(
        self,
        target_date: date = None,
        date_mode: str = "year",
        custom_target_date: date = None,
        custom_start_date: date = None,
        event_title: str = ""
    ):
        self.today = target_date or date.today()
        self.date_mode = date_mode
        self.event_title = (event_title or "").strip()

        # 1. Standard Year Mode Calculations
        self.date = self.today
        self.year = self.date.year
        self.day_of_year = self.date.timetuple().tm_yday
        self.is_leap_year = calendar.isleap(self.year)
        self.year_total_days = 366 if self.is_leap_year else 365
        self.year_days_remaining = self.year_total_days - self.day_of_year
        self.year_percentage_elapsed_exact = (self.day_of_year / self.year_total_days) * 100
        self.year_percentage_elapsed = round(self.year_percentage_elapsed_exact)
        self.year_percentage_remaining_exact = 100 - self.year_percentage_elapsed_exact
        self.year_percentage_remaining = round(self.year_percentage_remaining_exact)

        if self.date_mode == "custom" and custom_target_date is not None:
            self.target_date = custom_target_date
            self.start_date = custom_start_date or self.today

            # Ensure start_date <= target_date for calculation consistency
            if self.start_date > self.target_date:
                self.start_date = self.target_date

            self.days_remaining = max(0, (self.target_date - self.today).days)
            self.is_past = self.today >= self.target_date

            # Total duration of the countdown
            total_span = (self.target_date - self.start_date).days
            if total_span <= 0:
                # If start date is same as target date or ahead
                self.total_days = max(1, (self.target_date - self.today).days)
                self.days_elapsed = 0
                self.percentage_elapsed_exact = 0.0 if not self.is_past else 100.0
            else:
                self.total_days = total_span
                self.days_elapsed = max(0, (self.today - self.start_date).days)
                self.percentage_elapsed_exact = min(100.0, max(0.0, (self.days_elapsed / self.total_days) * 100))

            self.percentage_elapsed = round(self.percentage_elapsed_exact)
            self.percentage_remaining_exact = 100.0 - self.percentage_elapsed_exact
            self.percentage_remaining = round(self.percentage_remaining_exact)

            # day_of_period equivalent for dot rendering
            self.day_of_year = min(self.total_days, self.days_elapsed + 1)
        else:
            # Year mode defaults
            self.total_days = self.year_total_days
            self.days_remaining = self.year_days_remaining
            self.percentage_elapsed_exact = self.year_percentage_elapsed_exact
            self.percentage_elapsed = self.year_percentage_elapsed
            self.percentage_remaining_exact = self.year_percentage_remaining_exact
            self.percentage_remaining = self.year_percentage_remaining

    def to_dict(self):
        return {
            "date_mode": self.date_mode,
            "event_title": self.event_title,
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
            f"<DateStats mode={self.date_mode} title='{self.event_title}' "
            f"progress={self.day_of_year}/{self.total_days} "
            f"({self.percentage_elapsed}%) remaining={self.days_remaining}>"
        )


def parse_user_date(date_str: str) -> date | None:
    """
    Parses various date formats entered by user, e.g.:
    - '21st of January 2027', '21st January 2027', '21 January 2027'
    - 'January 21, 2027', 'Jan 21 2027'
    - '2027-01-21', '2027/01/21'
    - '21/01/2027', '21-01-2027'
    """
    if not date_str or not isinstance(date_str, str):
        return None

    cleaned = date_str.strip()
    if not cleaned:
        return None

    # Strip ordinal suffixes: 1st -> 1, 2nd -> 2, 3rd -> 3, 21st -> 21, 4th -> 4
    cleaned = re.sub(r'(\d+)(st|nd|rd|th)\b', r'\1', cleaned, flags=re.IGNORECASE)
    # Remove words like "of", "the", extra commas
    cleaned = re.sub(r'\b(of|the)\b', ' ', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'[,/.-]', ' ', cleaned)
    parts = cleaned.split()

    # Try common strptime patterns
    formats_to_try = [
        "%Y %m %d",
        "%d %m %Y",
        "%m %d %Y",
        "%d %B %Y",
        "%B %d %Y",
        "%d %b %Y",
        "%b %d %Y",
        "%Y %B %d",
        "%Y %b %d",
    ]

    reconstructed = " ".join(parts)
    for fmt in formats_to_try:
        try:
            dt = datetime.strptime(reconstructed, fmt)
            return dt.date()
        except ValueError:
            continue

    return None


def get_date_stats(
    target_date: date = None,
    date_mode: str = "year",
    custom_target_date: date = None,
    custom_start_date: date = None,
    event_title: str = ""
) -> DateStats:
    """Returns calculated day stats for target_date or custom countdown."""
    return DateStats(
        target_date=target_date,
        date_mode=date_mode,
        custom_target_date=custom_target_date,
        custom_start_date=custom_start_date,
        event_title=event_title
    )
