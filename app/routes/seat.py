from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.seat import Seat
from models.event import Event
from models.movie import Movie
from schemas.seat import SeatArrangementResponse, SeatResponse, BookSeatRequest, BookSeatResponse, EventResponse, CancelBookingRequest, CancelBookingResponse
from datetime import datetime, timedelta, timezone
import uuid

router = APIRouter()

@router.get("/events", response_model=list[EventResponse])
def get_available_events(db: Session = Depends(get_db)):
    # Get all events with movie details
    events = db.query(Event).join(Movie).all()
    
    event_responses = []
    for event in events:
        event_response = EventResponse(
            event_id=event.id,
            movie_title=event.movie.title,
            movie_description=event.movie.description,
            start_time=event.start_time
        )
        event_responses.append(event_response)
    
    return event_responses

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

@router.post("/book-seats", response_model=BookSeatResponse)
def book_seats(booking_request: BookSeatRequest, db: Session = Depends(get_db)):
    current_time = datetime.now(timezone.utc)
    
    # Check if all seats exist and are available
    seats = db.query(Seat).filter(Seat.id.in_(booking_request.seat_ids)).all()
    
    if len(seats) != len(booking_request.seat_ids):
        raise HTTPException(status_code=404, detail="One or more seats not found")
    
    # Check seat availability
    unavailable_seats = []
    total_amount = 0
    
    for seat in seats:
        current_status = seat.status
        
        # Check if locked seat has expired
        if seat.status == "locked" and seat.locked_at:
            time_diff = current_time - seat.locked_at.replace(tzinfo=timezone.utc)
            if time_diff.total_seconds() > 600:  # 10 minutes
                current_status = "open"
        
        if current_status != "open":
            unavailable_seats.append(seat.id)
        else:
            total_amount += seat.price
    
    if unavailable_seats:
        raise HTTPException(
            status_code=400, 
            detail=f"Seats {unavailable_seats} are not available"
        )
    
    # Lock the seats
    booking_reference = str(uuid.uuid4())[:8].upper()
    expires_at = current_time + timedelta(minutes=10)
    
    print(f"Generated booking_reference: {booking_reference}")
    
    for seat in seats:
        seat.status = "locked"
        seat.locked_at = current_time
        seat.booking_reference = booking_reference
        print(f"Setting seat {seat.id} booking_reference to: {booking_reference}")
    
    db.commit()
    print(f"Committed booking for seats: {booking_request.seat_ids}")
    
    return BookSeatResponse(
        booking_reference=booking_reference,
        seat_ids=booking_request.seat_ids,
        total_amount=total_amount,
        status="locked",
        expires_at=expires_at,
        message=f"Seats locked for 10 minutes. Complete payment before {expires_at.strftime('%H:%M:%S')}"
    )

@router.post("/cancel-booking", response_model=CancelBookingResponse)
def cancel_booking(cancel_request: CancelBookingRequest, db: Session = Depends(get_db)):
    print(f"Looking for booking_reference: {cancel_request.booking_reference}")
    
    # Find seats with this booking reference
    seats = db.query(Seat).filter(Seat.booking_reference == cancel_request.booking_reference).all()
    
    print(f"Found {len(seats)} seats with this booking reference")
    
    # Let's also check what booking references exist in the database
    all_booked_seats = db.query(Seat).filter(Seat.booking_reference.isnot(None)).all()
    print(f"All booking references in DB: {[seat.booking_reference for seat in all_booked_seats]}")
    
    if not seats:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Cancel the booking - reset seats to open
    cancelled_seat_ids = []
    for seat in seats:
        print(f"Cancelling seat {seat.id}")
        seat.status = "open"
        seat.locked_at = None
        seat.booking_reference = None
        cancelled_seat_ids.append(seat.id)
    
    db.commit()
    
    return CancelBookingResponse(
        booking_reference=cancel_request.booking_reference,
        cancelled_seat_ids=cancelled_seat_ids,
        message=f"Booking {cancel_request.booking_reference} has been cancelled. Seats are now available."
    )
