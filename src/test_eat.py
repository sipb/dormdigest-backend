import traceback
from pathlib import Path
from utils.email_parser import eat
from utils.category_parser import parse_tags

folder = "/home/k/sipb/dormspam/dormdigest-emails/emails_july_august"
email = None

count = 0
for file in Path(folder).iterdir():
    if not file.suffix == ".eml": continue

    with open(file, "r") as f:
        email = f.read()
    
    try:
        e = eat(email)
        if e.dormspam:
            count += 1
            print(e.thread_topic or e.subject, "->", parse_tags(e.categories))
    except:
        print(f"{file.name!r} had an error:")
        print(traceback.format_exc())
        print("---")

print(f"Found {count} email(s).")