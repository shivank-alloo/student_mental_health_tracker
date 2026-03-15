import joblib
import pandas as pd
import os

MODEL_PATH = "burnout_model.joblib"
model = None

def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
    else:
        print(f"Warning: Model file {MODEL_PATH} not found. Run ml_pipeline.py first.")

load_model()

def map_mood_to_int(mood_str):
    mood_str = mood_str.lower()
    if mood_str in ["sad", "stressed", "bad", "😢", "😭", "😠"]:
        return 0
    elif mood_str in ["ok", "neutral", "fine", "😐"]:
        return 1
    elif mood_str in ["happy", "good", "great", "excellent", "😁", "😃", "😊"]:
        return 2
    else:
        return 1 # Default to ok

def calculate_productivity_score(study_hours, sleep_hours, phone_hours, stress_level, mood_val):
    # This mirrors the logic in ml_pipeline.py for deterministic productivity scoring
    p_score = 50
    
    if 7 <= sleep_hours <= 9: p_score += 20
    else: p_score -= 10
    
    if 2 < study_hours <= 8: p_score += 20
    elif study_hours > 8: p_score -= (study_hours - 8) * 5
    
    if phone_hours > 3: p_score -= (phone_hours - 3) * 5
    
    if mood_val == 2: p_score += 10
    elif mood_val == 0: p_score -= 10
    
    if stress_level >= 4: p_score -= 10
    
    return max(0, min(100, p_score))

def get_suggestions(burnout_risk, productivity_score):
    suggestions = []
    
    if burnout_risk == "High":
        suggestions.append("🚨 HIGH BURNOUT RISK! Please take a full day off to rest.")
        suggestions.append("Listen to relaxing ambient or lo-fi music.")
    elif burnout_risk == "Medium":
        suggestions.append("You're pushing it. Schedule regular 15-minute breaks.")
    
    if productivity_score < 40:
        suggestions.append("Try the Pomodoro technique (25m study / 5m break) to boost focus.")
    elif productivity_score > 80:
        suggestions.append("You are in the zone! Keep up the momentum, but remember to stay hydrated.")
        
    if not suggestions:
        suggestions.append("Doing great! Maintain your current balanced routine.")
        
    return " | ".join(suggestions)

def predict_burnout(study_hours: float, sleep_hours: float, phone_hours: float, stress_level: int, mood_str: str):
    mood_val = map_mood_to_int(mood_str)
    
    if model is None:
        return "Unknown (Model not loaded)", 50.0, "Model not trained."
        
    input_data = pd.DataFrame({
        'study_hours': [study_hours],
        'sleep_hours': [sleep_hours],
        'phone_usage_hours': [phone_hours],
        'stress_level': [stress_level],
        'mood': [mood_val]
    })
    
    burnout_risk = model.predict(input_data)[0]
    productivity_score = calculate_productivity_score(study_hours, sleep_hours, phone_hours, stress_level, mood_val)
    suggestions = get_suggestions(burnout_risk, productivity_score)
    
    return burnout_risk, productivity_score, suggestions
