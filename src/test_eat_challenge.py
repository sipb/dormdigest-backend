from pathlib import Path
import requests

## Hint: Change folder to where you have the test emails stored!
folder = "/home/k/sipb/dormspam/dormdigest-emails/emails_july_august"

email = None

for file in Path(folder).iterdir():
    if not file.suffix == ".eml": continue

    with open(file, "r") as f:
        email = f.read()

    # Exercise 1: Parsing emails into your local database
    #             
    # To help you get more comfortable with API endpoints, 
    # you'll need to flesh out the remainder of this function.
    # It should take email files (ending in .eml extension)
    # in a given folder and then makes a POST request to 
    # `https://localhost:8432/eat` with the proper JSON body 
    # (see the API docs page on what format it is looking for)
    
    #
    # The /eat endpoint will parse in the emails for you
    # and store it in your local SQL database.
    #
    # Afterwards, you can then try viewing them by running
    # one of the API endpoints (like /get_events_by_date)
    # from the API docs:`https://localhost:8432/docs`
    
    pass