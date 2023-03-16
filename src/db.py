import sqlalchemy as db
from db_helpers import *
from schema import \
    session, Event, User
    
##############################################################
# Database Operations
##############################################################

# General Purpose Functions
def db_add(obj):
    """
    Add an object defined by the Schema to the database
    and commits the change

    Parameters
    ----------
    x : SQLBase
        The row object to add.
    """
    session.add(obj)
    session.commit()

## Get Functions

def get_all_events():
    '''Get information of all of events in database'''
    return session.query(Event).all()

## Add Functions
## TODO