from fastapi import FastAPI
import uvicorn
import db
from pydantic import BaseModel, ValidationError, validator
from datetime import date
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
    events_lst = db.get_events_by_month(req.month,req.year)
    return {
        'events': events_lst
    }
    
@app.post("/get_events_by_date")
async def get_events_by_date(req: GetEventsByDate):
    events_lst = db.get_events_by_date(req.from_date)
    return {
        'events': events_lst
    }

if __name__ == '__main__':
    uvicorn.run("main:app",
                host="localhost",
                port=8432,
                reload=True,
                ssl_keyfile="./src/configs/key.pem",
                ssl_certfile="./src/configs/cert.pem"
                )