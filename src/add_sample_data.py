from db import *
from random import randrange,randint
from datetime import timedelta
from emails.parse_type import CATEGORIES
import pprint

def get_random_date(start, end):
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
start_dates = [
    get_random_date(now,later) for i in range(len(event_and_clubs))
]
users = [
    'abc@mit.edu',
    'def@mit.edu',
]
tags = [
    [randint(0,10) for j in range(randint(1,3))] for i in range(len(event_and_clubs))
]
for user, start_time, event_and_club, tag_lst in zip(users,start_dates,event_and_clubs, tags):
    user_id = add_user(user)
    club_name, event_title, description = event_and_club
    club_id = add_club(club_name)
    
    assert user_id and club_id
    #event_id = add_event(event_title,user_id,description,start_time,tag_lst,club_id)
    #print(event_id)

for event in get_events_by_month(4,2023):
    #Using relationships
    event_tags = [x.get_tag_value() for x in event.tags.all()]
    print(event_tags)
    #Outputs: [5, 7, 9]
    
    #Alternatively,
    event_tags = get_event_tags(event.id)
    print(event_tags)
    #Outputs: [(5,), (7,), (9,)]