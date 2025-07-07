from fastapi import FastAPI
from database import engine, Base

# Import models so they get registered
from models import movie, event, seat

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movie Ticketing API")

@app.get("/")
def read_root():
    return {"message": "Movie Ticketing API is running"}
