import sqlalchemy as db
from sqlalchemy import exc
from datetime import timedelta, datetime

from db_helpers import *
from schema import \
    session, Event, EventTags, User
import calendar

MAX_COMMIT_RETRIES = 10

##############################################################
# Database Operations
##############################################################


## Get Functions
def get_all_events():
    '''Get information of all of events in database'''
    return list_dict_convert(session.query(Event).all())

def get_events_by_date(from_date):
    '''
    Get all events happening on a given day,
    ordered by start time and event name
    
    from_date: datetime object for target day
    '''
    to_date = from_date + timedelta(days=1)
    events = session.query(
            Event, EventTags
        ).filter(
            Event.id == EventTags.event_id 
        ).filter(
            Event.time_start.between(from_date, to_date)
        ).order_by(
            Event.time_start, Event.title
        ).all()
    return list_dict_convert(events)

def get_events_by_month(month,year=None):
    '''
    Get all events happening in a given month,
    ordered by start time and event name
    
    Month: int in range [0,12] inclusive
    Year: int (if None, will interpret as current year)

    '''
    assert 0 <= month <= 12, "Month must be in range 1 and 12"
    if not year:
        year = datetime.now().year
    _, last_day_of_month = calendar.monthrange(year,month)

    from_date = datetime(year,month,1)
    to_date = datetime(year,month,last_day_of_month)
    events = session.query(
            Event, EventTags
        ).filter(
            Event.id == EventTags.event_id 
        ).filter(
            Event.time_start.between(from_date, to_date)
        ).order_by(
            Event.time_start, Event.title
        ).all()
    return list_dict_convert(events)

## Add Functions
def add_event(title, user_id, description, time_start, club_id=None,\
              description_html=None, location=None, time_end=None, cta_link=None):
    '''
    Adds an event to the database
    
    Returns id of new event
    '''
    event = Event(None)
    #Required fields
    event.title = title
    event.user_id = user_id
    event.description = description
    event.time_start = time_start
    #Optional Fields
    event.club_id = club_id
    event.description_html = description_html
    event.location = location
    event.time_end = time_end
    event.cta_link = cta_link
    
    retry = 10
    committed = False
    while (not committed and retry > 0):
        try:
            session.add(event)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            event.generateUniques()
            retry -= 1
        else:
            committed = True
    if committed:
        session.flush()
        return event.id

def add_event_tags(event_id, event_tags):
    '''
    Given event_tags (list of ints representing enum Categories)
    and an event_id, link the event to those tags only
    
    Note: Will delete existing event_tags if they exist
    '''
    #Delete existing event_tags
    session.query(EventTags).filter(
            EventTags.event_id==event_id
        ).delete()
    
    #Create new event tags
    new_tags = []
    for tag in event_tags:
        new_tags.append(EventTags(event_id,tag))
    session.add_all(new_tags)
    session.commit()