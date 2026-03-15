from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import models
import schemas
import auth
import datetime
from database import engine, get_db
from predictor import predict_burnout

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Student Mental Health Tracker")

# Allow requests from our frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Student Mental Health Tracker API"}

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/entries/", response_model=schemas.DailyEntryResponse)
def create_entry(entry: schemas.DailyEntryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Restrict logging to evening/night before sleep (between 8 PM and 4 AM)
    current_time = datetime.datetime.now()
    if 4 <= current_time.hour < 20:
        raise HTTPException(
            status_code=400, 
            detail="To maintain data accuracy, please only log your daily data right before sleeping (between 8:00 PM and 4:00 AM)."
        )

    today_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + datetime.timedelta(days=1)
    
    existing_entry = db.query(models.DailyEntry).filter(
        models.DailyEntry.user_id == current_user.id,
        models.DailyEntry.date >= today_start,
        models.DailyEntry.date < today_end
    ).first()
    
    if existing_entry:
        raise HTTPException(status_code=400, detail="You have already logged your data for today.")

    burnout_risk, productivity_score, suggestions = predict_burnout(
        entry.study_hours,
        entry.sleep_hours,
        entry.phone_usage_hours,
        entry.stress_level,
        entry.mood
    )

    db_entry = models.DailyEntry(
        **entry.dict(),
        user_id=current_user.id,
        burnout_risk=burnout_risk,
        productivity_score=productivity_score,
        suggestions=suggestions
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@app.get("/entries/", response_model=list[schemas.DailyEntryResponse])
def get_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    entries = db.query(models.DailyEntry).filter(models.DailyEntry.user_id == current_user.id).order_by(models.DailyEntry.date.desc()).offset(skip).limit(limit).all()
    return entries
