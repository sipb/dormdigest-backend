#!/usr/bin/env python3

"""
For development purposes, you'll probably want to populate your local database
with a bunch of emails.  This script does just that -- populates the local SQL
database with random emails plus-or-minus one month or so.

To use this script, cd into `src` and run:

```bash
python3 utils/populate_db.py
```
"""

from pathlib import Path
import sys; sys.path.append(str(Path(sys.path[0]).parent))
import random
import datetime
from datetime import timedelta

import db.db_operations as db_operations
from utils.email_parser import Email, Contact, EmailAddress
from utils.category_parser import CATEGORIES

CATEGORIES = CATEGORIES[1:]

NUM_EMAILS = 200  # THIS MANY EMAILS TO ADD
LOWER_OFFSET = timedelta(days=-90)
UPPER_OFFSET = timedelta(days=60)

CONTACT = Contact(EmailAddress("example", "mit.edu"), "Tim Beaver")

WORDS = ["blah"] * 10
WORDS += ["blah.", "blah!", "blah?", "\n\n"]

def random_email(
   around: datetime.datetime,
   lower_offset: timedelta=timedelta(),
   upper_offset: timedelta=timedelta(),
   event_offset: timedelta=timedelta(days=7),
   subject: str="Subject line",
) -> Email:
   # generate email body
   words = list(WORDS)
   k = round(random.triangular(0, len(CATEGORIES)-1))
   categories = random.choices(CATEGORIES, k=k) if k else []
   for category in categories:
      words += [random.choice(category.keywords)]
   num_words = random.randint(10, len(words))
   body = " ".join([random.choice(words) for _ in range(num_words)])
   body += "\n\nbcc'd to dorms, græy for bc-talk"

   # start and end datetimes
   sent = around + lower_offset + random.random()*(upper_offset - lower_offset)
   when = ""
   if random.random() < 0.6:
      start_date = sent + event_offset
      when = "On " + start_date.strftime("%B %d, %Y")
      if random.random() < 0.8:
         start_time = (
            sent.replace(hour=0, minute=30)
            + random.random()*timedelta(hours=18)
         ).time()
         when += " at " + start_time.strftime("%H:%M")
         if random.random() < 0.4:
            end_time = start_time.replace(hour=start_time.hour+3)
            when += "-" + end_time.strftime("%H:%M")
   body = when + "\n\n" + body

   content = {"text/plain": body}

   email = Email(
      sent=sent,
      sender=CONTACT,
      subject=subject,
      thread_topic=subject,
      content=content,
      to=CONTACT,
      message_id=str(hash(body)),
   )
   return email

def main():
   today = datetime.datetime.now()
   mid = (LOWER_OFFSET + UPPER_OFFSET) / 2
   delta_t = (UPPER_OFFSET - mid) / NUM_EMAILS
   lower_offset = LOWER_OFFSET
   upper_offset = mid

   with db_operations.session_scope() as session:
      user_id = db_operations.add_user(session, str(CONTACT.email))
      for i in range(NUM_EMAILS):
         subject = f"Email #{i}/{NUM_EMAILS}"
         print(f"Generating {subject}...")
         lower_offset += delta_t
         upper_offset += delta_t
         email = random_email(today, lower_offset, upper_offset, subject=subject)

         when = email.when
         event_id = db_operations.add_event(
            session,
            email.thread_topic,
            user_id,
            description=email.plaintext,
            event_tags=list(email.categories | {0}),
            start_date=when.start_date or email.sent,
            start_time=when.start_time,
            end_date=when.end_date,
            end_time=when.end_time,
            date_created=email.sent,
         )

if __name__ == "__main__":
   main()



