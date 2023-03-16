import sys
import datetime
import re

from typing import Optional
from dataclasses import dataclass

# pattern that determines if it's a dormspam or not
DORMSPAM_PATTERN = r"\bbcc'?e?d\s+to\s+(all\s+)?dorms[;,]?\s+(\w+)\s+for bc-talk\b"

# supported email content types
CONTENT_TYPES = (
    "text/plain",
    "text/html",
)

# raised when the email could not be parsed
class EmailMissingHeaders(Exception): pass

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
    sender: str
    subject: str
    thread_topic: Optional[str]
    content: dict[str, str]
    to: Optional[str]
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
        ...

def html2text(html) -> str:
    """Convert html to plaintext
    """
    ...

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

    sent = datetime.datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
    
    content: dict[str, str] = {}
    for content_type in CONTENT_TYPES:
        match = re.search( # I'm not convinced this works for all emails
            rf"Content-Type: {content_type};.*?charset=.*?Content-Transfer-Encoding:.*?\n\n(.*?)(?=--)",
            raw,
            re.DOTALL,
        )
        if match:
            content[content_type] = match.group(1).strip()

    if not content:
        content_types = ", ".join(CONTENT_TYPES)
        msg = f"failed to parse email body (searched for {content_types})"
        raise EmailMissingHeaders(msg)

    return Email(
        sent=sent,
        sender=sender,
        subject=subject,
        thread_topic=thread_topic,
        content=content,
        to=to,
        message_id=message_id,
    )

if __name__ == "__main__":
    raw = sys.stdin.read()
    parsed_email = eat(raw)
    print("Parsed the email:")
    for k, v in parsed_email.__dict__.items():
        print(f"   {k!r} -> {v!r}")