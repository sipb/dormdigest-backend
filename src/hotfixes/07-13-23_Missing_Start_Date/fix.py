import sys
from datetime import datetime
from xxlimited import new
sys.path.append('/home/huydai/Documents/SIPB/dormdigest-backend/src') #Hardcoded

import db.db_operations as db_operations

def fix_missing_start_date():
    with db_operations.session_scope() as session:
        all_events = db_operations.get_all_events(session)
        for event in all_events:
            if not event.start_date: #MIME-encoding is only in emails with HTML description
                # By default set to be the day the email was created/received
                event.start_date = event.date_created.date()
                event.start_time = datetime.min.time()
        session.commit()
        session.flush()

if __name__ == '__main__':
    
    fix_missing_start_date()