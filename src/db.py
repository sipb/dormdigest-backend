import sqlalchemy as db
from sqlalchemy import exc
from datetime import timedelta, datetime

from db_helpers import *
from schema import \
    session, Event, EventTag, User, Club
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
            Event
        ).filter(
            Event.time_start.between(from_date, to_date)
        ).order_by(
            Event.time_start, Event.title
        ).all()
    return events

def get_events_by_month(month,year=None):
    '''
    Get all events happening in a given month,
    ordered by start time and event name
    
    Month: int in range [1,12] inclusive
    Year: int (if None, will interpret as current year)

    '''
    assert 1 <= month <= 12, "Month must be in range 1 and 12"
    if not year:
        year = datetime.now().year
    _, last_day_of_month = calendar.monthrange(year,month)

    from_date = datetime(year,month,1)
    to_date = datetime(year,month,last_day_of_month)
    events = session.query(
            Event
        ).filter(
            Event.time_start.between(from_date, to_date)
        ).order_by(
            Event.time_start, Event.title
        ).all()
    return events

def get_event_tags(event_id):
    '''
    Given an event_id, return list of all tags associated with it
    '''
    return session.query(EventTag.event_tag).filter(EventTag.event_id==event_id).all()

## Add Functions
def add_to_db(obj, others=None,rollbackfunc=None):
    """Adds objects to database with re-trials
    
    Arguments:
        obj {Model} -- Object(s) wanting to add
    
    Keyword Arguments:
        others {List} -- List of other model objects (default: {None})
        rollbackfunc {Func} -- Function that should be called on rollback (default: {None})
    
    Returns:
        Boolean - Success or not successful
    """
    global MAX_COMMIT_RETRIES
    retry = MAX_COMMIT_RETRIES
    committed = False
    while (not committed and retry > 0):
        try:
            session.add(obj)
            if (others):
                for o in others:
                    session.add(o)
            session.commit()
        except exc.IntegrityError:
            session.rollback()
            if (rollbackfunc):
                rollbackfunc()
            else:
                retry = 0
            retry -= 1
        else:
            committed = True
    return committed

def add_event(title, user_id, description, time_start, event_tags=[0],\
              club_id=None, description_html=None, location=None, \
              time_end=None, cta_link=None):
    '''
    Adds an event to the database
    
    Returns id of new event, or None if add failed
    '''
    event = Event()
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

    committed = add_to_db(event)
    if committed:
        session.flush()
        add_event_tags(event.id,event_tags)
        return event.id
    return None

def add_event_tags(event_id, event_tags):
    '''
    Given event_tags (list of ints representing enum Categories)
    and an event_id, link the event to those tags
    
    Note: Will delete existing event_tags if they exist
    '''
    #Delete existing event_tags
    session.query(EventTag).filter(
            EventTag.event_id==event_id
        ).delete()
    
    #Create new event tags
    new_tags = []
    for tag in event_tags:
        new_tags.append(EventTag(event_id,tag))
    session.add_all(new_tags)
    session.commit()
    
def add_user(email,user_privilege=0):
    '''
    Add a new user to the database (if it doesn't exist). 
    
    If user already exists with that email, returns id 
    of current user. Else, return id of new user, or None 
    if add failed.
    '''
    curr_user = session.query(User).filter(User.email==email).first()
    if curr_user:
        return curr_user.id
    
    new_user = User(email,user_privilege)
    committed = add_to_db(new_user)
    if committed:
        session.flush()
        return new_user.id
    return None

def add_club(club_name,club_abbrev=None,exec_email=None):
    '''
    Add a new club to the database (if it doesn't exist). 
    
    If a club already exists with that name, returns id 
    of current club. Else, return id of new club, or None
    if add failed.
    '''
    curr_club = session.query(Club).filter(Club.name==club_name).first()
    if curr_club:
        return curr_club.id
    print("No such club yet")
    
    new_club = Club(club_name,club_abbrev,exec_email)
    committed = add_to_db(new_club)
    
    if committed:
        session.flush()
        return new_club.id
    return None