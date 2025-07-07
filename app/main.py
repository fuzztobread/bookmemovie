from fastapi import FastAPI
from database import engine, Base
from routes.seat import router as seats_router

# Import ALL models explicitly so SQLAlchemy knows about them
from models.movie import Movie
from models.event import Event  
from models.seat import Seat

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movie Ticketing API")

# Include routers
app.include_router(seats_router, prefix="/api", tags=["seats"])

@app.get("/")
def read_root():
    return {"message": "Movie Ticketing API is running"}
