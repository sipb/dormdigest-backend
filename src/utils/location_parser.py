from __future__ import annotations
from dataclasses import dataclass
from typing import Set

from parser import Parser, ParserChain

LOCATIONS = [
   "Baker Dining", "Baker D",
   "MacGregor Dining", "MacGregor Dance Studio", "McCormick Dance Studio",
   "Burton Conner Porter Room", "BC Porter Room", "Porter Room",
   "McCormick Country Kitchen",
   "Lobby 7", "Lobby 10", "Lobby 13",
   "T-club", "Johnson Ice Rink", "Z-center", "Z center",
   "DuPont Wrestling Room", "DuPont",
   "Kresge", "Kresge Little Theatre", "Little Kresge", "Kresge Auditorium",
   "Stata", "Stata Lobby",
   "Student Center", "Lobdell",
   "Banana Lounge",
   "Talbot", "Talbot Lounge",
   "McDermott Court",
   "Sidney Pacific",
   "Athena Cluster",
   "Walker",
   "D-Lab",
   "Building 56",
   "Hei La Moon",
   "E51", "E62",
   "Media Lab",
]

@dataclass
class BldgRoom:
   bldg: str
   room: str

   def __str__(self): return f"{self.bldg}-{self.room}"

BLDG = r"(?P<bldg>[A-Z0-9]+)"
ROOM = r"(?P<room>[0-9][0-9][0-9])"

_parser_bldg_room = Parser[BldgRoom](
   BldgRoom,
   fr"\b{BLDG}[-–]{ROOM}\b",
   [str, str],
)

_parser_stata_bldg_room = Parser[BldgRoom](
   BldgRoom,
   fr"\b32[-–][GD]{ROOM}\b",
   [str, str],
)

LOCATION_PARSER_CHAIN = ParserChain[BldgRoom, str](
   [
      _parser_bldg_room,
      _parser_stata_bldg_room,
   ],
   lambda parsed: str(parsed)
)

def parse_locations(text: str) -> Set[str]:
   """Early iteration of a location parser

    Args:
        text: The body of text to search for locations.
   """
   locations = set(loc for loc in LOCATIONS if loc.lower() in text.lower())
   locations |= set(LOCATION_PARSER_CHAIN.iter(text))

   return locations

