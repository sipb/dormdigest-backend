from xml.etree.ElementInclude import include
from fastapi import (
    FastAPI,
    status, HTTPException,
)

from fastapi_cache import FastAPICache
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
import db.db_operations as db_operations
import db.schema as schema
from db.db_helpers import row2dict
from pydantic import BaseModel, ValidationError, validator
from datetime import date
import traceback
from collections import Counter

from utils.email_parser import eat, EmailMissingHeaders
import configs.server_configs as config # type: ignore
from configs.creds import valid_API_tokens

## Request Models
class GetEventsByMonth(BaseModel):
    month: int
    year: int | None = None
    
    @validator('month')
    def is_valid_month(cls, v):
        if not 1 <= v <= 12:
            raise ValueError("Month must be in range 1 and 12")
        return v
        
class GetEventsByDate(BaseModel):
    from_date: date
    include_description: bool | None = False

class EmailModel(BaseModel):
    email: str
    token: str

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_origins=["http://localhost:3000","https://localhost:3000","https://dormdigest.xvm.mit.edu"]
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/get_event_category_frequency_for_month")
async def get_event_category_frequency_for_month(req: GetEventsByMonth):
    '''
    Given the month and year, return a mapping of:
    - dates in the month which has at least one event, to
    - a frequency dictionary mapping tag names to the number of events the tag is used on that day
    '''
    with db_operations.session_scope() as session:
        events = db_operations.get_events_by_month(session,req.month,req.year)
        events_categories = db_operations.get_event_tags(session,events, convertName=True) #Make sure to get actual category names
        #print("Event categories",events_categories)
        event_categories_by_date = {} # Hold the tags used in each day
        
        # Sort events in bins of the day they start on,
        # keeping track of all event categories that are used on that day
        for (event, event_categories) in zip(events, events_categories):
            date = event.start_date.strftime("%Y-%m-%d")
            if date not in event_categories_by_date:
                event_categories_by_date[date] = event_categories.copy() #Memory safety
            else:
                event_categories_by_date[date].extend(event_categories)
        
        event_categories_freq_by_date = {} #Hold frequency of tags used on each day
        for (given_date, day_event_tags) in event_categories_by_date.items():
            event_categories_freq_by_date[given_date] = Counter(day_event_tags)
        
        return {
            'frequency': event_categories_freq_by_date
        }


@app.post("/get_events_by_month")
async def get_events_by_month(req: GetEventsByMonth):
    with db_operations.session_scope() as session:
        events = db_operations.get_events_by_month(session,req.month,req.year)
        tags = db_operations.get_event_tags(session,events)
        users = db_operations.get_event_user_emails(session,events)
        return {
            'events': row2dict(events),
            'tags': tags,
            'users': users
        }
    
@app.post("/get_events_by_date")
async def get_events_by_date(req: GetEventsByDate):
    with db_operations.session_scope() as session:
        events = db_operations.get_events_by_date(session,req.from_date)
        tags = db_operations.get_event_tags(session,events)
        users = db_operations.get_event_user_emails(session,events)
        res = {        
            'events': row2dict(events),
            'tags': tags,
            'users': users,
        }
        
        if req.include_description:
            descriptions = db_operations.get_event_descriptions(session,events,schema.EventDescriptionType.PLAINTEXT)
            descriptions_html = db_operations.get_event_descriptions(session,events,schema.EventDescriptionType.HTML)

            res['descriptions'] = descriptions
            res['descriptions_html'] = descriptions_html
        return res

@app.post("/eat", status_code=status.HTTP_201_CREATED)
async def digest(req: EmailModel):
    if not req.token in valid_API_tokens:
        msg = f"unrecognized token {req.token!r}"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg,
        )
    try:
        parsed = eat(req.email)
    except EmailMissingHeaders as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=tb,
        )

    verified = parsed.sender.email.domain.lower() == "mit.edu" # could be improved?
    sender_email = str(parsed.sender.email).lower()
    if verified and parsed.dormspam:
        with db_operations.session_scope() as session:
            user_id = db_operations.add_user(session, sender_email)
            club_id = None
            location = None
            for location in parsed.locations: break
            link = None

            event_id = db_operations.add_event(
                session,
                parsed.thread_topic or parsed.subject,
                user_id,
                parsed.plaintext,
                parsed.categories,
                parsed.when.start_date or parsed.sent.date(),
                parsed.when.end_date,
                parsed.when.start_time,
                parsed.when.end_time,
                parsed.content.get("text/html", None),
                club_id,
                location,
                link,
            )

if __name__ == '__main__':
    uvicorn.run("main:app",
                host=config.SERVER_HOST,
                port=config.SERVER_PORT,
                reload=False, #More optimized for production
                ssl_keyfile=config.SSL_KEY_FILE,
                ssl_certfile=config.SSL_CRT_FILE
                )
