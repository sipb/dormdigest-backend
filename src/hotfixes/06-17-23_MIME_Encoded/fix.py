import email
import sys
from xxlimited import new
sys.path.append('/home/huydai/Documents/SIPB/dormdigest-backend/src') #Hardcoded

import db.db_operations as db_operations
import quopri
import utils.email_parser as email_parser

def decode_events_description():
    with db_operations.session_scope() as session:
        all_events = db_operations.get_all_events(session)
        for event in all_events:
            if event.description_html: #MIME-encoding is only in emails with HTML description
                #print("Original HTML:\n",event.description_html)
                new_description_html = quopri.decodestring(event.description_html.encode('utf-8')).decode('utf-8',"ignore")
                #print("\n\nNew HTML:\n",new_description_html)
                event.description_html = new_description_html
                event.description = email_parser.html2text(new_description_html)
                #print("New plain",event.description)
        session.commit()
        session.flush()



if __name__ == '__main__':
    
    decode_events_description()