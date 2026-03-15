from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

class DailyEntryCreate(BaseModel):
    mood: str
    stress_level: int
    study_hours: float
    sleep_hours: float
    phone_usage_hours: float

class DailyEntryResponse(BaseModel):
    id: int
    date: datetime
    mood: str
    stress_level: int
    study_hours: float
    sleep_hours: float
    phone_usage_hours: float
    burnout_risk: Optional[str] = None
    productivity_score: Optional[float] = None
    suggestions: Optional[str] = None

    class Config:
        from_attributes = True
