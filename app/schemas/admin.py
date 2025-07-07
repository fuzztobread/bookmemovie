from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Movie schemas
class CreateMovieRequest(BaseModel):
    title: str
    description: Optional[str] = None

class UpdateMovieRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class MovieResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    
    class Config:
        from_attributes = True

# Event/Showtime schemas
class CreateEventRequest(BaseModel):
    movie_id: int
    start_time: datetime
    total_seats: int = 25  # Default 5x5 grid

class UpdateEventRequest(BaseModel):
    movie_id: Optional[int] = None
    start_time: Optional[datetime] = None

class EventAdminResponse(BaseModel):
    id: int
    movie_id: int
    movie_title: str
    start_time: datetime
    total_seats: int
    booked_seats: int
    locked_seats: int
    available_seats: int
    
    class Config:
        from_attributes = True

class DeleteResponse(BaseModel):
    message: str
    deleted_id: int
