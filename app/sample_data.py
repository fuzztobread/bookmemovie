from database import SessionLocal, engine, Base
from models.movie import Movie
from models.event import Event
from models.seat import Seat
from datetime import datetime, timedelta, timezone

# Create all tables first
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Add a sample movie
movie = Movie(
    title="Avengers: Endgame",
    description="The epic conclusion to the Infinity Saga"
)
db.add(movie)
db.commit()
db.refresh(movie)

# Add a sample event (showtime)
event = Event(
    movie_id=movie.id,
    start_time=datetime.now(timezone.utc) + timedelta(hours=2)
)
db.add(event)
db.commit()
db.refresh(event)

# Add sample seats (simple 5x5 grid)
for row in ['A', 'B', 'C', 'D', 'E']:
    for seat_num in range(1, 6):
        price = 15.0 if row in ['A', 'B'] else 12.0  # Front rows cost more
        seat = Seat(
            event_id=event.id,
            price=price,
            description=f"Row {row} Seat {seat_num}",
            status="open"
        )
        db.add(seat)

db.commit()

# Get IDs before closing session
movie_id = movie.id
event_id = event.id

db.close()

print(f"Sample data added!")
print(f"Movie ID: {movie_id}")
print(f"Event ID: {event_id}")
print("Added 25 seats (5x5 grid)")
