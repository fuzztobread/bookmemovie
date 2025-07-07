from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)  # This is the seat_id
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(255), nullable=False)  # Like "Row A Seat 1"
    status = Column(String(20), default="open")  # open, locked, booked
    locked_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    event = relationship("Event", back_populates="seats")
