from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    entries = relationship("DailyEntry", back_populates="owner")

class DailyEntry(Base):
    __tablename__ = "daily_entries"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="entries")
    
    # Inputs
    mood = Column(String) # Emoji or text category
    stress_level = Column(Integer) # Perceived stress (1 to 5)
    study_hours = Column(Float)
    sleep_hours = Column(Float)
    sleep_bedtime = Column(String) # When the user went to sleep
    sleep_quality = Column(Integer) # Quality score (1-5)
    phone_usage_hours = Column(Float)
    comment = Column(String) # User notes/comments
    
    # ML Predictions
    burnout_risk = Column(String) # e.g., "High", "Medium", "Low"
    productivity_score = Column(Float) # e.g., 0.0 to 1.0 (or 0-100)
    suggestions = Column(String) # JSON or comma-separated string of suggestions
