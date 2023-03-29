import sqlalchemy as db
from db_helpers import *
from schema import \
    session, Event, User
    
##############################################################
# Database Operations
##############################################################


## Get Functions

def get_all_events():
    '''Get information of all of events in database'''
    return session.query(Event).all()

## Add Functions
## TODO