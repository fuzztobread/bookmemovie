from pydantic import BaseModel
from typing import List
from datetime import datetime

class SeatResponse(BaseModel):
    seat_id: int
    price: float
    description: str
    status: str  # open, locked, booked
    
    class Config:
        from_attributes = True

class SeatArrangementResponse(BaseModel):
    event_id: int
    seats: List[SeatResponse]

class BookSeatRequest(BaseModel):
    seat_id: int
    user_email: str  # Simple auth for now
