from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Set
import re

@dataclass
class Category:
   keywords: List[str]
   name: str
   info: Optional[str] = None


OTHER = Category([], "OTHER", "Default category")

FOOD = Category(
   [
      "cookie", "food", "eat", "study break", "boba", "bubble tea", "chicken",
      "bonchon", "bon chon", "bertucci", "pizza", "sandwich", "leftover",
      "salad", "burrito", "dinner provided", "lunch provided",
      "breakfast provided", "dinner included", "lunch included", "ramen",
      "kbbq", "dumplings", "waffles", "csc", "dim sum", "drink",
   ],
   "FOOD"
)

CAREER = Category(
   ["career", "summer plans", "internship", "xfair", "recruiting",],
   "CAREER",
   "Career and recruiting events held by companies on campus."
)

FUNDRAISING = Category(
   ["donate", "donated", "donation",],
   "FUNDRAISING",
   "Events that benefit a cause."
)

APPLICATION = Category(
   [
      "apply", "application", "join", "deadline", "sign up", "audition",
      "application",
   ],
   "APPLICATION",
   "For joining or applying for something."
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
   "PERFORMANCE",
   "Dance, music, a capella, and other concerts and performances."
)

BOBA = Category(
   ["boba", "bubble tea", "kung fu tea", "kft", "teado", "tea do",],
   "BOBA"
)

TALKS = Category(
   [
      "discussion", "q&a", "tech talk", "recruiting", "info session",
      "information session", "infosession", "workshop", "research",
   ],
   "TALKS",
   "Talks, workshops, short classes."
)

SALE = Category(
   [
      "sale", "selling", 
   ],
   "SALE",
   "Selling things, senior sales."
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
   SALE,
]

def parse_categories(text: str) -> Set[int]:
   """An iteration of a category parser

   Returns a set of ``int``s, because the database stores category information
   as such.

   Args:
      text: The body of text to search for locations.
   """
   categories = set()
   for i, category in enumerate(CATEGORIES):
      for keyword in category.keywords:
         pattern = fr"\b{re.escape(keyword)}\b"
         match = re.search(pattern, text, re.IGNORECASE)
         if match:
            categories.add(i)
            break

   return categories

def parse_tags(tags: list[int]) -> list[str]:
   """Convert tag numbers to corresponding category names
   
   Return a list of unique category names
   
   Args:
      tags: The list of tags associated with an event/events
   """
   category_names = [CATEGORIES[tag].name for tag in tags]
   return category_names
