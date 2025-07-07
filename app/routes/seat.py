from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.seat import Seat
from models.event import Event
from schemas.seat import SeatArrangementResponse, SeatResponse
from datetime import datetime, timedelta, timezone

router = APIRouter()

@router.get("/events/{event_id}/seats", response_model=SeatArrangementResponse)
def get_seats_for_event(event_id: int, db: Session = Depends(get_db)):
    # Check if event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Get all seats for this event
    seats = db.query(Seat).filter(Seat.event_id == event_id).all()
    
    # Convert seats to response format
    seat_responses = []
    current_time = datetime.now(timezone.utc)
    
    for seat in seats:
        # Determine current status - handle expired locks
        current_status = seat.status
        
        # If seat is locked, check if lock has expired
        if current_status == "locked" and seat.locked_at:
            time_diff = current_time - seat.locked_at.replace(tzinfo=timezone.utc)
            if time_diff.total_seconds() > 600:  # 600 seconds = 10 minutes
                current_status = "open"
        
        seat_response = SeatResponse(
            seat_id=seat.id,
            price=seat.price,
            description=seat.description,
            status=current_status
        )
        seat_responses.append(seat_response)
    
    return SeatArrangementResponse(
        event_id=event_id,
        seats=seat_responses
    )
