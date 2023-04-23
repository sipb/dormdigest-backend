from fastapi import FastAPI
import uvicorn
import db
from pydantic import BaseModel, ValidationError, validator
from datetime import date
import configs.server_configs as config

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

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/get_events_by_month")
async def get_events_by_month(req: GetEventsByMonth):
    events = db.get_events_by_month(req.month,req.year)
    tags = db.get_event_tags(events)
    return {
        'events': events,
        'tags': tags
    }
    
@app.post("/get_events_by_date")
async def get_events_by_date(req: GetEventsByDate):
    events = db.get_events_by_date(req.from_date)
    tags = db.get_event_tags(events)
    return {
        'events': events,
        'tags': tags
    }

if __name__ == '__main__':
    uvicorn.run("main:app",
                host=config.SERVER_HOST,
                port=config.SERVER_PORT,
                reload=False, #More optimized for production
                ssl_keyfile=config.SSL_KEY_FILE,
                ssl_certfile=config.SSL_CRT_FILE
                )