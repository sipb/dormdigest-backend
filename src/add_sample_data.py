from db import *
from random import randrange,randint
from datetime import timedelta
from schema import MemberPrivilege
from emails.parse_type import CATEGORIES

def get_random_datetime(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

now = datetime.now()
later = now + timedelta(weeks=4)

event_and_clubs = [
    ("Vietnamese Student Association","VSA Potluck","Come eat food"),
    ("SIPB","Machine Room Tour","Watch how servers run, wohoo!")
]
start_date_and_time = [
    get_random_datetime(now,later) for i in range(len(event_and_clubs))
]
users = [
    'abc@mit.edu',
    'def@mit.edu',
]
tags = [
    [randint(0,10) for j in range(randint(1,3))] for i in range(len(event_and_clubs))
]
for user, start_datetime, event_and_club, tag_lst in zip(users,start_date_and_time,event_and_clubs, tags):
    user_id = add_user(user)
    club_name, event_title, description = event_and_club
    club_id = add_club(club_name)
    
    assert user_id and club_id
    add_club_member(club_id,user_id,MemberPrivilege.OFFICER.value)
    #event_id = add_event(event_title,user_id,description,event_tags=tag_lst,club_id=club_id,
    #                     start_date=start_datetime.date(),
    #                     start_time=start_datetime.time())
    
    #print(event_id)

month_res = get_events_by_month(4,2023)
for event in month_res:
    #Using relationships
    event_tags = [x.get_tag_value() for x in event.tags.all()]
    print(event_tags)
    #Outputs: [5, 7, 9]
    
print(get_event_tags(month_res))