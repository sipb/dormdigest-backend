from typing import Optional, Set, List, Tuple
from dataclasses import dataclass

import sys
import datetime
import re
import base64
import quopri
import html.parser

from .parser import Parser, ParserChain
from .time_parser import parse_event_time, EventTime
from .location_parser import parse_locations
from .category_parser import parse_categories

# pattern that determines if it's a dormspam or not
DORMSPAM_PATTERN = r"\bbcc'?e?d\s+to\s+(all\s+)?dorms[;,.]?\s+(\w+)\s+for bc-talk\b"
DORMSPAM_PATTERN_COLOR_GROUP = 2

# supported email content types
CONTENT_TYPES = (
    "text/plain",
    "text/html",
)

# raised when the email could not be parsed
class EmailMissingHeaders(Exception): pass

class HTML2TextConverter(html.parser.HTMLParser):
    """Used to convert any HTML to plaintext

    Example: ::

        >>> html = "<h1>Some header</h1><p>Some text</p>"
        >>> parser = HTML2TextConverter()
        >>> parser.feed(html)
        >>> print(parser.get_text())
        Some header
        Some text
        >>> 
    """
    entities = {
        "nbsp": " ",
        "lt": "<",
        "gt": ">",
        "amp": "&",
        "quot": "\"",
        "apos": "'",
    }

    def __init__(self) -> None:
        html.parser.HTMLParser.__init__(self)
        self.text_parts: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]) -> None:
        if tag == "br":
            self.text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6"):
            self.text_parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.text_parts.append(data)

    def handle_entityref(self, name: str) -> None:
        self.text_parts.append(self.entities.get(name, ""))

    def get_text(self) -> str:
        return "".join(self.text_parts).strip()

def html2text(html: str) -> str:
    """Convert html to plaintext
    """
    parser = HTML2TextConverter()
    parser.feed(html)
    return parser.get_text()

@dataclass
class EmailAddress:
    username: str
    domain: str
    def __str__(self) -> str:
        return f"{self.username}@{self.domain}"

@dataclass
class Contact:
    """Email address with an optional name
    """
    email: EmailAddress
    name: Optional[str] = None
    def __str__(self) -> str:
        email_part = f"<{self.email}>"
        if not self.name: return email_part
        return f"{self.name} {email_part}"

_parser_email_address = Parser[EmailAddress](
    EmailAddress,
    r"^(?P<username>[a-zA-Z0-9._%+-]+)@(?P<domain>[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$",
    [str, str],
)
_parser_full_email_address = Parser[Contact](
    Contact,
    r"^(?P<name>.+)\s+<(?P<email>.+)>$",
    [_parser_email_address, str],
)

def parse_contact(text: str) -> Contact:
    """Parses sender or recipient info

    Raises:
        EmailMissingHeaders: if text could not be parsed
    """
    full_email = _parser_full_email_address(text)
    if full_email: return full_email
    plain_email = _parser_email_address(text)
    if plain_email: return Contact(plain_email)

    msg = f"failed to parse {text!r} as email"
    raise EmailMissingHeaders(msg)

@dataclass(kw_only=True)
class Email:
    """Represents a digested email

    Attributes:
        sent: When the email was sent
        sender: By whom the email was sent
        subject: Email subject line
        thread_topic: Email thread topic, used by email systems to group related messages together
        content: Dictionary mapping the supported content types to what was found in the email
        to: Who the email was sent to, if anyone.
        message_id: Universal ID of the email.
    """
    sent: datetime.datetime
    sender: Contact
    subject: str
    thread_topic: Optional[str]
    content: dict[str, str]
    to: Optional[Contact]
    message_id: str

    @property
    def plaintext(self) -> str:
        if "text/plain" in self.content:
            return self.content["text/plain"]
        elif "text/html" in self.content:
            return html2text(self.content["text/html"])
        return ""

    @property
    def dormspam(self) -> bool:
        return bool(self.color)

    @property
    def color(self) -> Optional[str]:
        search = re.search(DORMSPAM_PATTERN, self.plaintext, flags=re.IGNORECASE)
        if search: return search.group(DORMSPAM_PATTERN_COLOR_GROUP)
        return None

    @property
    def when(self) -> EventTime:
        return parse_event_time(self.plaintext, today=self.sent.date())

    @property
    def locations(self) -> Set[str]:
        return parse_locations(self.plaintext)

    @property
    def categories(self) -> Set[int]:
        return parse_categories(self.plaintext)

def nibble(header: str, pattern: str, raw: str, headers_not_found: Optional[list[str]]=None) -> Optional[str]:
    """Digest a single header from the email
    """
    search = re.search(pattern, raw)
    if search: return search.group(1)
    if headers_not_found: headers_not_found.append(header)
    return None

def eat(raw) -> Email:
    """Digest a raw email

    Raises:
        EmailMissingHeaders: if some headers could not be parsed
    """
    # keep track of what couldn't be found
    headers_not_found: list[str] = []

    # eat it one bite at a time
    message_id   = nibble(   "Message-ID",    r"Message-ID:\s+<(.*?)>",     raw, headers_not_found)
    date         = nibble(         "Date",          r"Date:\s+(.*?)(?=\n)", raw, headers_not_found)
    sender       = nibble(         "From",          r"From:\s+(.*?)(?=\n)", raw, headers_not_found)
    subject      = nibble(      "Subject",       r"Subject:\s+(.*?)(?=\n)", raw, headers_not_found)
    thread_topic = nibble( "Thread-Topic",  r"Thread-Topic:\s+(.*?)(?=\n)", raw)
    to           = nibble("X-Original-To", r"X-Original-To:\s+(.*?)(?=\n)", raw)

    if headers_not_found:
        headers = ", ".join([repr(header) for header in headers_not_found])
        msg = f"failed to parse: {headers}"
        raise EmailMissingHeaders(msg)

    # keep my type checker quiet
    assert(message_id is not None)
    assert(date is not None)
    assert(sender is not None)
    assert(subject is not None)
    assert(to is not None)

    # parse emails
    sender_contact = parse_contact(sender)
    to_contact = parse_contact(to)

    sent = datetime.datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
    
    content: dict[str, str] = {}
    for content_type in CONTENT_TYPES:
        match = re.search( # I'm not *entirely* convinced this works for all emails
            rf"Content-Type: {content_type};.*?charset=.*?Content-Transfer-Encoding:(.*?)\n\n(.*?)(?=--)",
            raw,
            re.DOTALL,
        )
        if match:
            encoding = match.group(1).strip()
            message = match.group(2).strip()
            if encoding == "base64":
                message = base64.b64decode(message).decode("utf-8")
            elif encoding == "quoted-printable":
                message = quopri.decodestring(message).decode("utf-8")

            content[content_type] = message

    if not content:
        content_types = ", ".join(CONTENT_TYPES)
        msg = f"failed to parse email body (searched for {content_types})"
        raise EmailMissingHeaders(msg)

    return Email(
        sent=sent,
        sender=sender_contact,
        subject=subject,
        thread_topic=thread_topic,
        content=content,
        to=to_contact,
        message_id=message_id,
    )

if __name__ == "__main__":
    raw = sys.stdin.read()
    parsed_email = eat(raw)
    print("Parsed the email:")
    for k, v in parsed_email.__dict__.items():
        print(f"   {k!r} -> {v!r}")
    
    print(f"   'color' -> {parsed_email.color!r}")
    print(f"   'dormspam' -> {parsed_email.dormspam!r}")
    print(f"   'when' -> {parsed_email.when!r}")
    print(f"   'locations' -> {parsed_email.locations!r}")
    print(f"   'categories' -> {parsed_email.categories!r}")

    pass
