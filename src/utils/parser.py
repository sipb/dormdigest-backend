from __future__ import annotations
from dataclasses import dataclass
from typing import (
    Callable, Generator, Iterator, Tuple, List, Dict, Any,
    Optional, Union, Final, Generic, TypeVar,
)
A = TypeVar("A")
B = TypeVar("B")

import re

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

    def iter(self, text: str) -> Iterator[A]:
        """Iterate through all matches found
        """
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
                yield parsed

        return None

    def __call__(self, text: str) -> Optional[A]:
        """Return first match
        """
        parsed = None
        for parsed in self.iter(text): break
        return parsed

    def __str__(self):
        return self.pattern

@dataclass
class ParserChain(Generic[A, B]):
    parsers: List[Parser]
    formatter: Callable[[A], B]

    def iter(self, text: str, **kwargs) -> Iterator[B]:
        """Iterate through all matches found
        """
        for parser in self.parsers:
            for parsed in parser.iter(text):
                yield self.formatter(parsed, **kwargs)

    def __call__(self, text: str, **kwargs) -> Optional[B]:
        """Return first match
        """
        formatted = None
        for formatted in self.iter(text, **kwargs): break
        return formatted
