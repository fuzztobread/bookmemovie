from pydantic import BaseModel
from typing import List
from datetime import datetime

class EventResponse(BaseModel):
    event_id: int
    movie_title: str
    movie_description: str
    start_time: datetime
    
    class Config:
        from_attributes = True

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
    seat_ids: List[int]
    user_email: str

class BookSeatResponse(BaseModel):
    booking_reference: str
    seat_ids: List[int]
    total_amount: float
    status: str
    expires_at: datetime
    message: str

class CancelBookingRequest(BaseModel):
    booking_reference: str

class CancelBookingResponse(BaseModel):
    booking_reference: str
    cancelled_seat_ids: List[int]
    message: str

class PaymentRequest(BaseModel):
    booking_reference: str
    payment_success: bool  # True for success, False for failure

class PaymentResponse(BaseModel):
    booking_reference: str
    payment_status: str  # "success" or "failed"
    seat_ids: List[int]
    message: str
