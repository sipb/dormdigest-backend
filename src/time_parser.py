from __future__ import annotations
from dataclasses import dataclass
from typing import (
    Callable, Tuple, List, Dict, Any,
    Optional, Union, Final, Generic, TypeVar,
)
A = TypeVar("A")
B = TypeVar("B")

import re
import datetime

@dataclass
class Parser(Generic[A]):
    """Represents a regex parser to extract info from text

    The assembled ``Parser[NamedTuple]`` object can be called on a string
    (``text``) to attempt the parsing. If successful, it returns the parsed
    data as the ``NamedTuple`` type. Otherwise returns `None`.

    Attributes:
        output: The type of the parsed output, if successful.
        pattern: The regex pattern to search for. The respective regex named
            groups correspond exactly to the ``NamedTuple`` fields.
        subparsers: The respective functions or parsers to call on for the
            extracted group text.
        tweak: Any additional finishing touches to perform on the returned
            info.
    """
    output: type
    pattern: str
    subparsers: List[Union[Parser, Callable[[str], Any]]]
    tweak: Callable[[A], Optional[A]] = lambda parsed: parsed

    def __post_init__(self) -> None:
        if hasattr(self.output, "__annotations__"):
            self.annotations = self.output.__annotations__
        else:
            self.annotations = self.output.__origin__.__annotations__
        assert self.annotations, \
            f"original output type {self.output!r} must have type annotations"

    def __call__(self, text: str) -> Optional[A]:
        for match in re.finditer(self.pattern, text, flags=re.IGNORECASE):
            groups = match.groupdict()
            kwargs = {}
            successfully_parsed = True
            for i, name in enumerate(self.annotations):
                value = self.subparsers[i](groups[name])
                if value is None:
                    successfully_parsed = False
                    break
                kwargs[name] = value
            if not successfully_parsed: continue

            parsed = self.output(**kwargs)
            parsed = self.tweak(parsed)
            if parsed is not None:
                return parsed

        return None

    def __str__(self):
        return self.pattern

@dataclass
class ParserChain(Generic[A, B]):
    parsers: List[Parser]
    formatter: Callable[[A], B]

    def __call__(self, text: str, **kwargs) -> Optional[B]:
        for parser in self.parsers:
            parsed = parser(text)
            if parsed is not None:
                return self.formatter(parsed, **kwargs)
        return None

TODAY = datetime.date.today()

# non-numerical names for months or hours
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
HOURS: Final[Dict[str, int]] = {
    "Noon": 12,
    "Midnight": 0,
}

@dataclass
class MonthNameDay:
    month_name: str
    day: int

@dataclass
class MonthDay:
    month: int
    day: int

Date = Union[MonthNameDay, MonthDay]

_parser_month_name_day = Parser[MonthNameDay](
    MonthNameDay,
    r"(?P<month_name>\w+)\s+(?P<day>\d{1,2})",
    [str, int],
    lambda parsed: parsed if parsed.month_name.capitalize() in MONTHS else None,
)
_parser_day_month_name = Parser[MonthNameDay](
    MonthNameDay,
    r"(?P<day>\d{1,2})\s+(?P<month_name>\w+)",
    [str, int],
    lambda parsed: parsed if parsed.month_name.capitalize() in MONTHS else None,
)
_parser_month_day = Parser[MonthDay](
    MonthDay,
    r"(?P<month>\d{1,2})\/(?P<day>\d{1,2})",
    [int, int],
)

def _format_month_name_day(parsed: MonthNameDay, *, today: datetime.date=TODAY) -> datetime.date:
    return datetime.date(
        today.year,
        MONTHS[parsed.month_name.capitalize()],
        parsed.day,
    )

def _format_month_day(parsed: MonthDay, *, today: datetime.date=TODAY) -> datetime.date:
    return datetime.date(today.year, parsed.month, parsed.day)

_date_formatters = {
    MonthNameDay: _format_month_name_day,
    MonthDay: _format_month_day,
}

def format_date(parsed: Date, *, today: datetime.date=TODAY) -> datetime.date:
    date = _date_formatters[type(parsed)](parsed, today=today)
    if date < today: date = date.replace(year=date.year+1)
    return date

DATE_PARSER_CHAIN = ParserChain[Date, datetime.date](
    [
        _parser_month_name_day,
        _parser_day_month_name,
        _parser_month_day,
    ],
    format_date,
)


@dataclass
class HourOnly:
    hour: int

@dataclass
class HourMinute:
    hour: int
    minute: int

@dataclass
class HourMinutePeriod:
    hour: int
    minute: int
    period: str

@dataclass
class HourName:
    hour_name: str

Time = Union[HourOnly, HourMinute, HourMinutePeriod, HourName]

@dataclass
class TimeRange(Generic[A, B]):
    start: A
    end: B

HH = r"(?P<hour>\d{1,2})"                # h or hh
MM = r"(?::(?P<minute>\d{2}))"           # :mm
PERIOD = r"(?:(?P<period>a|p)\.?m?\.?)" # a, am, a.m.

_parser_hour_only = Parser[HourOnly](HourOnly, fr"\b{HH}\b", [int])
_parser_hour_period = Parser[HourMinutePeriod](
    HourMinutePeriod,
    fr"\b{HH}{MM}?\s*{PERIOD}\b",
    [int, lambda mm: 0 if mm is None else int(mm), str],
)
_parser_hour_minute = Parser[HourMinutePeriod](
    HourMinutePeriod,
    fr"\b{HH}{MM}\s*{PERIOD}?\b",
    [int, int, lambda period: "a" if period is None else str(period)],
)
_parser_hour_name = Parser[HourName](
    HourName,
    r"\b(?P<hour_name>noon|midnight)\b",
    [lambda name: name.capitalize()],
)

def _format_hour_only(parsed: HourOnly) -> datetime.time:
    return datetime.time(parsed.hour)

def _format_hour_minute(parsed: HourMinute) -> datetime.time:
    return datetime.time(parsed.hour, parsed.minute)

def _format_hour_minute_period(parsed: HourMinutePeriod) -> datetime.time:
    h = parsed.hour
    m = parsed.minute if parsed.minute is not None else 0

    if parsed.period is None:
        return datetime.time(h, m)

    period = parsed.period.lower()
    if period == "p" and h < 12:
        h += 12
    elif period == "a" and h == 12:
        h = 0

    return datetime.time(h, m)

def _format_hour_name(parsed: HourName) -> datetime.time:
    return datetime.time(HOURS[parsed.hour_name])

_time_formatters = {
    HourOnly: _format_hour_only,
    HourMinute: _format_hour_minute,
    HourMinutePeriod: _format_hour_minute_period,
    HourName: _format_hour_name,
}

def format_time(parsed: Time) -> datetime.time:
    return _time_formatters[type(parsed)](parsed)

TIME_PARSER_CHAIN = ParserChain(
    [
        _parser_hour_period,
        _parser_hour_minute,
        _parser_hour_name,
    ],
    format_time,
)

TIME_RANGE_PATTERN = r"\b(?P<start>\S+)\b\s*(?:[-–]|to|until)\s*\b(?P<end>\S+)\b"

def format_time_range(parsed: TimeRange) -> Tuple[datetime.time, datetime.time]:
    return (
        format_time(parsed.start),
        format_time(parsed.end),
    )

TIME_RANGE_PARSER_CHAIN = ParserChain[TimeRange, Tuple[datetime.time, datetime.time]](
    [
        Parser[TimeRange[HourOnly, HourMinutePeriod]]( # 10-10:30
            TimeRange[HourOnly, HourMinutePeriod],
            TIME_RANGE_PATTERN,
            [_parser_hour_only, _parser_hour_minute],
        ),
        Parser[TimeRange[HourMinutePeriod, HourOnly]]( # 10:30-11
            TimeRange[HourMinutePeriod, HourOnly],
            TIME_RANGE_PATTERN,
            [_parser_hour_minute, _parser_hour_only],
        ),
        Parser[TimeRange[HourMinutePeriod, HourMinutePeriod]]( # 10:00-11:00
            TimeRange[HourMinutePeriod, HourMinutePeriod],
            TIME_RANGE_PATTERN,
            [_parser_hour_minute, _parser_hour_minute],
        ),
        Parser[TimeRange[HourOnly, HourMinutePeriod]]( # 10-11am
            TimeRange[HourOnly, HourMinutePeriod],
            TIME_RANGE_PATTERN,
            [_parser_hour_only, _parser_hour_period],
        ),
        Parser[TimeRange[HourMinutePeriod, HourMinutePeriod]]( # 10am-11am
            TimeRange[HourMinutePeriod, HourMinutePeriod],
            TIME_RANGE_PATTERN,
            [_parser_hour_period, _parser_hour_period],
        ),
        Parser[TimeRange[HourMinutePeriod, HourMinutePeriod]]( # 10:30-11am
            TimeRange[HourMinutePeriod, HourMinutePeriod],
            TIME_RANGE_PATTERN,
            [_parser_hour_minute, _parser_hour_period],
        ),
        Parser[TimeRange[HourMinutePeriod, HourName]]( # 10:30-noon
            TimeRange[HourMinutePeriod, HourName],
            TIME_RANGE_PATTERN,
            [_parser_hour_minute, _parser_hour_name],
        ),
        Parser[TimeRange[HourMinutePeriod, HourName]]( # 10am-noon
            TimeRange[HourMinutePeriod, HourName],
            TIME_RANGE_PATTERN,
            [_parser_hour_period, _parser_hour_name],
        ),
    ],
    format_time_range,
)

@dataclass
class EventTime:
    start_date: Optional[datetime.date]
    start_time: Optional[datetime.time]
    end_date: Optional[datetime.date]
    end_time: Optional[datetime.time]

def parse_event_time(text: str, *, today: datetime.date=TODAY) -> EventTime:
    """Early iteration of an event time parser

    It has room for improvement, but it works.

    Args:
        text: The body of text to search for event times.
    """
    # dates
    date = DATE_PARSER_CHAIN(text, today=today)

    # times
    time_range = TIME_RANGE_PARSER_CHAIN(text)
    if time_range is None:
        start_time = TIME_PARSER_CHAIN(text)
        end_time = None
    else:
        start_time, end_time = time_range

    return EventTime(
        date,
        start_time,
        None if end_time is None else date,
        end_time,
    )

if __name__ == "__main__":
    text = "It's from 8am-noon on March 17!"
    print(text)
    print(parse_event_time(text))