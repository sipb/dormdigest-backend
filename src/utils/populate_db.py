#!/usr/bin/env python3

"""
For development purposes, you'll probably want to populate your local database
with a bunch of emails.  This script does just that -- populates the local SQL
database with random emails plus-or-minus one month or so.

To use this script, cd into `src` and run:

```bash
# see help leaflet for more details
python3 utils/populate_db.py

# add session ID for tbeaver, and add 10 random emails
python3 utils/populate_db.py "tbeaver@mit.edu" -e 10 -s
```

Example output:

```
Generating Email #0/10...
Generating Email #1/10...
Generating Email #2/10...
Generating Email #3/10...
Generating Email #4/10...
Generating Email #5/10...
Generating Email #6/10...
Generating Email #7/10...
Generating Email #8/10...
Generating Email #9/10...
Added this session ID for tbeaver@mit.edu: '8bb763d6d3785a2ae205901be1b44a8e'
Done.
```

"""

from pathlib import Path
import sys; sys.path.append(str(Path(sys.path[0]).parent))
import random
import datetime
from datetime import timedelta
import argparse

import db.db_operations as db_operations
from utils.email_parser import Email, Contact, EmailAddress
from utils.category_parser import CATEGORIES

CATEGORIES = CATEGORIES[1:]

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
   sender: Contact=CONTACT,
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
      sender=sender,
      subject=subject,
      thread_topic=subject,
      content=content,
      to=CONTACT,
      message_id=str(hash(body)),
   )
   return email

def add_events(num_events: int=200, sender: Contact=CONTACT):
   today = datetime.datetime.now()
   mid = (LOWER_OFFSET + UPPER_OFFSET) / 2
   delta_t = (UPPER_OFFSET - mid) / num_events
   lower_offset = LOWER_OFFSET
   upper_offset = mid

   with db_operations.session_scope() as session:
      for i in range(num_events):
         subject = f"Email #{i}/{num_events}"
         print(f"Generating {subject}...")
         lower_offset += delta_t
         upper_offset += delta_t

         this_sender = sender if random.randint(0, 1) else CONTACT
         user_id = db_operations.add_user(session, str(this_sender.email))

         email = random_email(today,
            lower_offset, upper_offset, subject=subject,
            sender=this_sender)

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

def add_session_id(email: str, session_id: str):
   with db_operations.session_scope() as session:
      token = session_id if session_id != "" else None
      token = str(db_operations.add_session_id(session, email, token))
      print(f"Added this session ID for {email}: {token!r}")

def main():
   parser = argparse.ArgumentParser(
      prog="populate_db.py",
      description="Quickly populate your local DormDigest database.",
   )
   parser.add_argument("email", type=str, metavar="EMAIL")
   parser.add_argument("-e", "--events", type=int, metavar="NUM_EVENTS",
      help=(
         "Add this many events to the database.  Half of the added events "
         "will use the provided email as the author, with the other half "
         "using 'Tim Beaver' as the author."
      ),
   )
   parser.add_argument("-s", "--session-id", type=str, nargs="?", const="",
      help=(
         "Add a session ID to the email in the database.  If no session ID is "
         "specified, a random one is generated.  In any case, the script will "
         "always inform you of the token that was added before exiting."
      ),
   )
   args = parser.parse_args()
   #print(args)

   actions = 0
   if isinstance(args.events, int) and args.events > 0:
      add_events(args.events, Contact(args.email, "User"))
      actions += 1
   if isinstance(args.session_id, str):
      add_session_id(args.email, args.session_id)
      actions += 1

   if not actions: print("Nothing to do...")
   print("Done.")

if __name__ == "__main__":
   main()
   



