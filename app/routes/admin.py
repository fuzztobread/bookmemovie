from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.movie import Movie
from models.event import Event
from models.seat import Seat
from schemas.admin import (
    CreateMovieRequest, UpdateMovieRequest, MovieResponse,
    CreateEventRequest, UpdateEventRequest, EventAdminResponse,
    DeleteResponse
)
from datetime import datetime, timezone

router = APIRouter()

# ============ MOVIE MANAGEMENT ============

@router.get("/movies", response_model=list[MovieResponse])
def get_all_movies(db: Session = Depends(get_db)):
    """Get all movies"""
    movies = db.query(Movie).all()
    return movies

@router.post("/movies", response_model=MovieResponse)
def create_movie(movie_request: CreateMovieRequest, db: Session = Depends(get_db)):
    """Create a new movie"""
    movie = Movie(
        title=movie_request.title,
        description=movie_request.description
    )
    
    db.add(movie)
    db.commit()
    db.refresh(movie)
    
    return movie

@router.put("/movies/{movie_id}", response_model=MovieResponse)
def update_movie(movie_id: int, movie_request: UpdateMovieRequest, db: Session = Depends(get_db)):
    """Update an existing movie"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Update only provided fields
    if movie_request.title is not None:
        movie.title = movie_request.title
    if movie_request.description is not None:
        movie.description = movie_request.description
    
    db.commit()
    db.refresh(movie)
    
    return movie

@router.delete("/movies/{movie_id}", response_model=DeleteResponse)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    """Delete a movie and all its events"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Check if movie has events
    events = db.query(Event).filter(Event.movie_id == movie_id).all()
    
    if events:
        # Delete all seats for all events of this movie
        for event in events:
            db.query(Seat).filter(Seat.event_id == event.id).delete()
        
        # Delete all events
        db.query(Event).filter(Event.movie_id == movie_id).delete()
    
    # Delete the movie
    db.delete(movie)
    db.commit()
    
    return DeleteResponse(
        message=f"Movie '{movie.title}' and all its events have been deleted",
        deleted_id=movie_id
    )

# ============ EVENT/SHOWTIME MANAGEMENT ============

@router.get("/events", response_model=list[EventAdminResponse])
def get_all_events_admin(db: Session = Depends(get_db)):
    """Get all events with detailed information"""
    events = db.query(Event).join(Movie).all()
    
    event_responses = []
    for event in events:
        # Get seat statistics
        seats = db.query(Seat).filter(Seat.event_id == event.id).all()
        
        total_seats = len(seats)
        booked_seats = len([s for s in seats if s.status == "booked"])
        locked_seats = len([s for s in seats if s.status == "locked"])
        available_seats = total_seats - booked_seats - locked_seats
        
        event_response = EventAdminResponse(
            id=event.id,
            movie_id=event.movie_id,
            movie_title=event.movie.title,
            start_time=event.start_time,
            total_seats=total_seats,
            booked_seats=booked_seats,
            locked_seats=locked_seats,
            available_seats=available_seats
        )
        event_responses.append(event_response)
    
    return event_responses

@router.post("/events", response_model=EventAdminResponse)
def create_event(event_request: CreateEventRequest, db: Session = Depends(get_db)):
    """Create a new event/showtime and generate seats"""
    
    # Check if movie exists
    movie = db.query(Movie).filter(Movie.id == event_request.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Create event
    event = Event(
        movie_id=event_request.movie_id,
        start_time=event_request.start_time,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # Generate seats automatically
    seats_created = create_seats_for_event(event.id, event_request.total_seats, db)
    
    return EventAdminResponse(
        id=event.id,
        movie_id=event.movie_id,
        movie_title=movie.title,
        start_time=event.start_time,
        total_seats=seats_created,
        booked_seats=0,
        locked_seats=0,
        available_seats=seats_created
    )

@router.put("/events/{event_id}", response_model=EventAdminResponse)
def update_event(event_id: int, event_request: UpdateEventRequest, db: Session = Depends(get_db)):
    """Update an existing event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Update only provided fields
    if event_request.movie_id is not None:
        # Check if new movie exists
        movie = db.query(Movie).filter(Movie.id == event_request.movie_id).first()
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        event.movie_id = event_request.movie_id
    
    if event_request.start_time is not None:
        event.start_time = event_request.start_time
    
    db.commit()
    db.refresh(event)
    
    # Get updated seat statistics
    seats = db.query(Seat).filter(Seat.event_id == event.id).all()
    total_seats = len(seats)
    booked_seats = len([s for s in seats if s.status == "booked"])
    locked_seats = len([s for s in seats if s.status == "locked"])
    available_seats = total_seats - booked_seats - locked_seats
    
    return EventAdminResponse(
        id=event.id,
        movie_id=event.movie_id,
        movie_title=event.movie.title,
        start_time=event.start_time,
        total_seats=total_seats,
        booked_seats=booked_seats,
        locked_seats=locked_seats,
        available_seats=available_seats
    )

@router.delete("/events/{event_id}", response_model=DeleteResponse)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Delete an event and all its seats"""
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if event has bookings
    seats = db.query(Seat).filter(Seat.event_id == event_id).all()
    booked_seats = [s for s in seats if s.status == "booked"]
    
    if booked_seats:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete event. {len(booked_seats)} seats are already booked."
        )
    
    # Delete all seats for this event
    db.query(Seat).filter(Seat.event_id == event_id).delete()
    
    # Delete the event
    movie_title = event.movie.title
    db.delete(event)
    db.commit()
    
    return DeleteResponse(
        message=f"Event for '{movie_title}' has been deleted",
        deleted_id=event_id
    )

# ============ HELPER FUNCTIONS ============

def create_seats_for_event(event_id: int, total_seats: int, db: Session):
    """Helper function to create seats for an event"""
    
    # Calculate grid size (try to make it roughly square)
    import math
    rows = int(math.sqrt(total_seats))
    cols = math.ceil(total_seats / rows)
    
    # Generate seat letters (A, B, C, ...)
    seat_letters = [chr(65 + i) for i in range(rows)]  # A=65 in ASCII
    
    seats_created = 0
    
    for row_idx, row_letter in enumerate(seat_letters):
        for seat_num in range(1, cols + 1):
            if seats_created >= total_seats:
                break
            
            # Price based on row (front rows more expensive)
            if row_idx < rows // 3:  # First third - premium
                price = 18.0
            elif row_idx < 2 * rows // 3:  # Middle third - standard
                price = 15.0
            else:  # Back third - economy
                price = 12.0
            
            seat = Seat(
                event_id=event_id,
                price=price,
                description=f"Row {row_letter} Seat {seat_num}",
                status="open"
            )
            
            db.add(seat)
            seats_created += 1
        
        if seats_created >= total_seats:
            break
    
    db.commit()
    return seats_created
