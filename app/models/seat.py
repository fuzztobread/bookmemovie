from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone

class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)  #seat_id
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(255), nullable=False)  #row-column name
    status = Column(String(20), default="open")  # open, locked, booked
    locked_at = Column(DateTime, nullable=True)
    booking_reference = Column(String(50),nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationship
    event = relationship("Event", back_populates="seats")
