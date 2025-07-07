from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500))

    # Relationship
    events = relationship("Event", back_populates="movie")
