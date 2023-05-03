from fastapi import (
    FastAPI,
    status, HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import db
from pydantic import BaseModel, ValidationError, validator
from datetime import date

from utils.email_parser import eat, EmailMissingHeaders
import configs.server_configs as config # type: ignore

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

class EmailModel(BaseModel):
    email: str
    token: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"],
    allow_origins=["*"]
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/get_events_by_month")
async def get_events_by_month(req: GetEventsByMonth):
    events = db.get_events_by_month(req.month,req.year)
    tags = db.get_event_tags(events)
    db.session.close()
    return {
        'events': events,
        'tags': tags
    }
    
@app.post("/get_events_by_date")
async def get_events_by_date(req: GetEventsByDate):
    events = db.get_events_by_date(req.from_date)
    tags = db.get_event_tags(events)
    db.session.close()
    return {
        'events': events,
        'tags': tags
    }

@app.post("/eat")
async def digest(req: EmailModel, status_code=201):
    if req.token != config.TOKEN:
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

    verified = parsed.sender.email.domain.lower() == "mit.edu" # could be improved?
    sender_email = str(parsed.sender.email).lower()

    if verified:
        user_id = db.add_user(sender_email)
        club_id = None
        location = None
        for location in parsed.locations: break
        link = None

        event_id = db.add_event(
            parsed.thread_topic,
            user_id,
            parsed.plaintext,
            parsed.categories,
            parsed.when.start_date,
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
