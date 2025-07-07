from fastapi import FastAPI
from app.database import engine, Base

from app.models import movie, event, seat

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movie Ticketing API")

@app.get("/")
def read_root():
    return {"message": "Movie Ticketing API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0",port=8000)
