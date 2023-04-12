from fastapi import FastAPI
import uvicorn
import os

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    uvicorn.run("main:app",
                host="localhost",
                port=8432,
                reload=True,
                ssl_keyfile="./src/configs/key.pem",
                ssl_certfile="./src/configs/cert.pem"
                )