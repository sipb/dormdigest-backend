import re
import datetime

from dataclasses import dataclass
from typing import Callable, Final, Tuple, List, Dict, Optional

@dataclass
class EventTime:
    start: Tuple[Optional[datetime.date], Optional[datetime.time]]
    end: Tuple[Optional[datetime.date], Optional[datetime.time]]

@dataclass
class Pattern:
    """Represents a pattern to look for

    Attributes:
        pattern: The regex pattern to search for
        groups: The respective names corresponding to the regex pattern groups
        checks: Any additional checks to perform for respective args
    """
    pattern: str
    groups: Tuple[str,...]
    checks: Dict[str, Callable[[str], bool]]

    def __call__(self, text: str) -> Optional[Dict[str, str]]:
        for match in re.finditer(self.pattern, text, flags=re.IGNORECASE):
            if not match: continue
            kwargs = {}
            for group_name, group in zip(self.groups, match.groups()):
                if group is not None:
                    kwargs[group_name] = group

            failed_checks = False
            for key, check in self.checks.items():
                if not check(kwargs[key]):
                    failed_checks = True
                    break

            if failed_checks: continue

            return kwargs

        return None

TODAY = datetime.date.today()

MONTHS: Final[Dict[str, int]] = {
    "January":   1,     "Jan": 1,
    "February":  2,     "Feb": 2,
    "March":     3,     "Mar": 3,
    "April":     4,     "Apr": 4,
    "May":       5,     "May": 5,
    "June":      6,     "Jun": 6,
    "July":      7,     "Jul": 7,
    "August":    8,     "Aug": 8,
    "September": 9,     "Sep": 9,
    "October":   10,    "Oct": 10,
    "November":  11,    "Nov": 11,
    "December":  12,    "Dec": 12,
}

DATE_PATTERNS: Final[List[Pattern]] = [
    Pattern(r"(\w+)\s+(\d{1,2})",    ("month_name", "day"), {"month_name": lambda x: x.capitalize() in MONTHS}),
    Pattern(r"(\d{1,2})\s+(\w+)",    ("day", "month_name"), {"month_name": lambda x: x.capitalize() in MONTHS}),
    Pattern(r"(\d{1,2})\/(\d{1,2})", ("month", "day"),      {}),
]
TIME_RANGE_PATTERN: Final[str] = r"\b(\S+)\b\s*(?:[-–]|to|until)\s*\b(\S+)\b"
TIME_PATTERNS: Final[List[Pattern]] = [
    Pattern(r"(\d{1,2})(?::(\d{2}))?\s*((?:a|p)\.?m?\.?)?\b", ("hour", "minute", "am_pm"), {}),
    Pattern(r"\b(noon|midnight)\b", ("special",), {}),
]
SPECIAL_TIMES = {"noon": 12, "midnight": 0}

def format_time(**kwargs: str) -> datetime.time:
    """Format a time given some combination of arguments

    Keyword args:
        hour: Optional.
        minute: Optional.
        am_pm: "am" or "pm". Optional.

    Raises:
        ValueError: If a respective arg cannot be converted to an int.
        TypeError: If neither `hour` nor `special` is supplied
    """
    if "special" in kwargs:
        h = SPECIAL_TIMES[kwargs["special"].lower()]
    elif "hour" in kwargs:
        h = int(kwargs["hour"])
    else:
        raise TypeError("either 'hour' or 'special' must be supplied")

    m = int(kwargs["minute"]) if "minute" in kwargs else 0
    am_pm = kwargs.get("am_pm", "").lower().replace(".", "")

    if am_pm in ("pm", "p") and h != 12:
        h += 12
    elif am_pm in ("am", "a") and h == 12:
        h = 0

    return datetime.time(h, m)

def format_date(*, day: str, today=TODAY, **kwargs: str) -> datetime.date:
    """Format a date given some combination of arguments

    Keyword args:
        month: Month number, where 1 represents January. Required if `month_name` is not supplied.
        month_name: e.g. "January". Required if `month` is not supplied.

    Raises:
        ValueError: If a respective arg cannot be converted to an int.
        TypeError: If neither `month` nor `month_name` is supplied
    """
    if "month" in kwargs:
        m = int(kwargs["month"])
    elif "month_name" in kwargs:
        month_name = kwargs["month_name"]
        m = MONTHS.get(month_name.capitalize())
        if m is None:
            raise ValueError(f"invalid month name: {month_name!r}")
    else:
        raise TypeError("either 'month' or 'month_name' must be supplied")

    d = int(day)
    
    # if the parsed date has already passed in the current year,
    # then assume it's in the next calendar year
    y = today.year
    parsed_date = datetime.date(y, m, d)
    if parsed_date < today: y += 1
        
    return datetime.date(y, m, d)

def parse_event_time(text: str, today: datetime.date=TODAY) -> EventTime:
    """Early iteration of an event time parser

    It has room for improvement, but it works.

    Args:
        text: The body of text to search for event times.
    """
    # dates
    date = None
    for date_pattern in DATE_PATTERNS:
        kwargs = date_pattern(text)
        if kwargs is not None:
            date = format_date(**kwargs, today=today)
            break

    # time
    start_time = None
    end_time = None
    match = re.search(TIME_RANGE_PATTERN, text, flags=re.IGNORECASE)
    if match:
        # time range
        for time_pattern in TIME_PATTERNS:
            start_kwargs = time_pattern(match.groups()[0])
            if start_kwargs is not None:
                start_time = format_time(**start_kwargs)
                break
        for time_pattern in TIME_PATTERNS:
            end_kwargs = time_pattern(match.groups()[1])
            if end_kwargs is not None:
                end_time = format_time(**end_kwargs)
                break
    else:
        # single time
        for time_pattern in TIME_PATTERNS:
            start_kwargs = time_pattern(text)
            if start_kwargs is not None:
                start_time = format_time(**start_kwargs)

    start = (date, start_time)
    end = (date, end_time)

    return EventTime(start, end)

if __name__ == "__main__":
    text = "It's from 8am-noon on March 17!"
    print(text)
    print(parse_event_time(text))