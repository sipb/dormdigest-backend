import sys
import datetime
sys.path.append('/home/huydai/Documents/SIPB/dormdigest-backend/src') #Hardcoded

import db.db_operations as db_operations

def fix_one_year_start_date():
    with db_operations.session_scope() as session:
        all_events = db_operations.get_all_events(session)
        for event in all_events:
            if event.start_date and event.start_date.year != 2023: #Wrong year
                # Set date to be this year
                #print("Before",event.start_date)
                #print("After",event.start_date - datetime.timedelta(days=366))
                event.start_date = event.start_date - datetime.timedelta(days=366)
        session.commit()
        session.flush()

if __name__ == '__main__':
    fix_one_year_start_date()