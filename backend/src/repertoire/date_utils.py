from datetime import UTC, date, datetime, time, timedelta


def start_of_utc_day(moment: date) -> datetime:
    return datetime.combine(moment, time.min, tzinfo=UTC)


def current_week_bounds(today: date) -> tuple[datetime, datetime]:
    """[start, end) for the current ISO week (Monday-start), in UTC.

    A session exactly at Monday 00:00:00 UTC counts as this week; a session
    at the following Monday 00:00:00 UTC belongs to next week (excluded).
    """
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=7)
    return start_of_utc_day(start_date), start_of_utc_day(end_date)
