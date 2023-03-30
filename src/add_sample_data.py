from db import *
from random import randrange
from datetime import timedelta

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

for user, start_time, event_and_club in zip(users,start_dates,event_and_clubs):
    user_id = add_user(user)
    club_name, event_title, description = event_and_club
    club_id = add_club(club_name)
    
    assert user_id and club_id
    event_id = add_event(event_title,user_id,description,start_time,club_id)
    print(event_id)