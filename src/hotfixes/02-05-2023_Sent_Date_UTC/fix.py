import sys
import os
from zoneinfo import ZoneInfo
sys.path.append('/home/sipb/dormdigest-backend/src') #Hardcoded
os.chdir('/home/sipb/dormdigest-backend/src')

import db.db_operations as db_operations

def fix_bad_email_sent_datetime():
    with db_operations.session_scope() as session:
        all_events = db_operations.get_all_events(session)
        for event in all_events:
            if event.date_created:
                print("Before",event.date_created)
                event.date_created = event.date_created.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo('America/New_York'))
                print("After",event.date_created)
        session.commit()
        session.flush()

if __name__ == '__main__':
    fix_bad_email_sent_datetime()
