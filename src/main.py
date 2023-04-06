from fastapi import FastAPI
from utils.email_parser import eat

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/eat")
async def digest():
    """
    """

@app.get("/get")
async def get_emails():
    """
    """