from typing import Any, Optional, Set, List, Tuple
from dataclasses import dataclass


import sys
import datetime
import re
import html.parser
import mailparser

# Image processing
from PIL import Image
import base64
from io import BytesIO
from pillow_heif import register_heif_opener

# Image saving
import uuid
import os

from .parser import Parser, ParserChain
from .time_parser import parse_event_time, EventTime
from .location_parser import parse_locations
from .category_parser import parse_categories
from configs.server_configs import BASE_IMAGE_URL, LOCAL_IMAGE_PATH

# pattern that determines if it's a dormspam or not
DORMSPAM_PATTERN = r"\b[bB]cc[’'`-]?e?d\s+to\s+(all\s+)?(?:dorms|dormspam)[;,.]?\s+([\*\s\w-]+)\s+for bc-talk\b"
DORMSPAM_PATTERN_COLOR_GROUP = 2

# supported email content types
CONTENT_TYPES = (
    "text/plain",
    "text/html",
)

# Compressing images
COMPRESSED_IMAGE_WIDTH = 500 # pixels

#Enable Pillow plugin to support HEIC images
register_heif_opener() 

def generate_image_name():
    name = f"{uuid.uuid1()}.png"
    return name

def check_duplicate(image_path):
    return os.path.exists(image_path)

def compress_image_and_save(original_image: str) -> str:
    '''
    Given a base64 encoding of an image, resize the image such that it is 500 x * pixels in size
    (keeping aspect ratio), and compress it using Pillow's `optimize` and `quality` flags.

    Returns url of the image
    '''
    img = Image.open(BytesIO(base64.b64decode(original_image)))
    #Calculate new image size
    wpercent = (COMPRESSED_IMAGE_WIDTH/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    # Resize the image
    img = img.resize((COMPRESSED_IMAGE_WIDTH,hsize), Image.Resampling.LANCZOS)
    # Generate a unique name for the image using uuid1
    image_name = generate_image_name()
    image_path = LOCAL_IMAGE_PATH + image_name
    while check_duplicate(image_path):
        image_name = generate_image_name()
        image_path = LOCAL_IMAGE_PATH + image_name
    img.save(image_path, optimize=True, quality=80, format='PNG')
    return BASE_IMAGE_URL+image_name


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
        if search:
            return search.group(DORMSPAM_PATTERN_COLOR_GROUP)
        return None

    @property
    def when(self) -> EventTime:
        return parse_event_time(self.plaintext, today=self.sent.date())

    @property
    def locations(self) -> Set[str]:
        return parse_locations(self.plaintext)

    @property
    def categories(self) -> Set[int]:
        text = f"{self.thread_topic or self.subject}\n\n{self.plaintext}"
        return parse_categories(text)

def nibble(header_name: str, header_data: Any, headers_not_found: Optional[list[str]]=None) -> Any:
    """Digest a single header from the email
    """
    if header_data:
        return header_data
    if headers_not_found is not None:
        headers_not_found.append(header_name)
    return None

def parse_date(date: str) -> datetime.datetime:
    fmt = "%a, %d %b %Y %H:%M:%S %z"
    try:
        sent = datetime.datetime.strptime(date, fmt)
    except ValueError as v:
        extra = v.args[0].partition("unconverted data remains: ")[-1]
        if not extra: raise
        sent = datetime.datetime.strptime(date[:-len(extra)], fmt)

    return sent

ContactsType = list[tuple[str,str]]

def eat(raw) -> Email:
    """Digest a raw email

    Raises:
        EmailMissingHeaders: if some headers could not be parsed
    """
    email = mailparser.parse_from_string(raw)
    assert(isinstance(email, mailparser.MailParser))

    # keep track of what couldn't be found
    headers_not_found: list[str] = []

    # eat it one bite at a time
    message_id: str               = nibble("Message-ID", email.message_id, headers_not_found)
    sent:       datetime.datetime = nibble(      "Date", email.date+'Z',       headers_not_found) #Note: We add "Z" to indicate that it's UTC time
    sender:     ContactsType      = nibble(      "From", email.from_,      headers_not_found)
    subject:    str               = nibble(   "Subject", email.subject,    headers_not_found)
    to:         ContactsType      = nibble(        "To", email.to)

    if headers_not_found:
        headers = ", ".join([repr(header) for header in headers_not_found])
        msg = f"failed to parse: {headers}"
        raise EmailMissingHeaders(msg)

    # optional headers
    thread_topic = None if "Thread-Topic" not in email.headers else email.headers["Thread-Topic"]

    # keep my type checker quiet
    assert(message_id is not None)
    assert(sent is not None)
    assert(subject is not None)
    assert(sender is not None)

    # by default, we fetch the first contact listed in "From:" and "To:"
    first_sender_name, first_sender_email = sender[0] # (name, email)
    first_to_name, first_to_email = None, None
    if to is not None: first_to_name, first_to_email = to[0]

    # theoretically, sender's email should always be filled out, but not necessarily to's email
    # if the To spot is empty, `first_to_email` is an empty string
    sender_contact = Contact(_parser_email_address(first_sender_email), first_sender_name)
    to_contact = None
    if first_to_name or first_to_email:
        to_contact = Contact(_parser_email_address(first_to_email), first_to_name)

    # parse email body, and process inserted images
    content = {}

    if email.text_plain:
        content["text/plain"] = email.text_plain[0]
        for attachment in email.attachments:
            if cid := attachment["content-id"].strip("<>"):
                before = f"[cid:{cid}]"
                after = ""
                content["text/plain"] = content["text/plain"].replace(before, after)

    if email.text_html:
        content["text/html"] = email.text_html[0]
        for attachment in email.attachments:
            if cid := attachment["content-id"].strip("<>"):
                cte = attachment.get("content_transfer_encoding") or "base64"
                before = f'src="cid:{cid}"'
                payload_fixed = attachment["payload"].replace("\n","")
                #Proceed to compress and save if attachment is an image
                if 'mail_content_type' in attachment and attachment['mail_content_type'].startswith("image/"):
                    payload_image_url = compress_image_and_save(payload_fixed)
                    after = f'''src="{payload_image_url}"'''
                    content["text/html"] = content["text/html"].replace(before, after) #change the cid with the basic c4 encoding of the image

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
