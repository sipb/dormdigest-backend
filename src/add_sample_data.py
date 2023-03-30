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
    ("VSA Potluck","Vietnamese Student Association","Come eat food"),
    ("Machine Room Tour","Student Information Processing Board","Watch how servers run, wohoo!")
]
start_dates = [
    get_random_date(now,later) for i in range(len(event_and_clubs))
]
users = [
    'sipb-ec@mit.edu',
    'mitvsa-officers@mit.edu',
]
