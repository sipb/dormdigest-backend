from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Set

@dataclass
class Category:
   keywords: List[str]
   info: Optional[str] = None

OTHER = Category([], "Default category")

FOOD = Category(
   [
      "cookie", "food", "eat", "study break", "boba", "bubble tea", "chicken",
      "bonchon", "bon chon", "bertucci", "pizza", "sandwich", "leftover",
      "salad", "burrito", "dinner provided", "lunch provided",
      "breakfast provided", "dinner included", "lunch included", "ramen",
      "kbbq", "dumplings", "waffles", "csc", "dim sum", "drink",
   ],
)

CAREER = Category(
   ["career", "summer plans", "internship", "xfair", "recruiting",],
   "Career and recruiting events held by companies on campus."
)

FUNDRAISING = Category(
   ["donate", "donated", "donation",],
   "Events that benefit a cause.",
)

APPLICATION = Category(
   [
      "apply", "application", "join", "deadline", "sign up", "audition",
      "application",
   ],
   "For joining or applying for something.",
)

PERFORMANCE = Category(
   [
      "orchestra", "shakespeare", "theatre", "theater", "tryout", "audition",
      "muses", "serenade", "syncopasian", "ohms", "logarhythms",
      "chorallaries", "symphony", "choir", "concert", "ensemble", "jazz",
      "resonance", "a capella", "toons", "sing", "centrifugues", "dancetroupe",
      "adt", "asian dance team", "mocha moves", "ridonkulous", "donk",
      "fixation", "bhangra", "roadkill", "vagina monologues", "24 hour show",
      "acappella", "admission", "ticket",
   ],
   "Dance, music, a capella, and other concerts and performances.",
)

BOBA = Category(
   ["boba", "bubble tea", "kung fu tea", "kft", "teado", "tea do",],
)

TALKS = Category(
   [
      "discussion", "q&a", "tech talk", "recruiting", "info session",
      "information session", "infosession", "workshop", "research",
   ],
   "Talks, workshops, short classes.",
)

# as they're stored in the database
CATEGORIES = [
   OTHER,
   FOOD,
   CAREER,
   FUNDRAISING,
   APPLICATION,
   PERFORMANCE,
   BOBA,
   TALKS,
]

def parse_categories(text: str) -> Set[int]:
   """Early iteration of a category parser

   Returns a set of ``int``s, because the database stores category information
   as such.

   Args:
        text: The body of text to search for locations.
   """
   text = text.lower()
   categories = set(
      i for i, category in enumerate(CATEGORIES)
      if any(keyword.lower() in text for keyword in category.keywords)
   )

   return categories

