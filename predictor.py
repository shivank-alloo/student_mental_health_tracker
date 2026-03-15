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

def calculate_productivity_score(study_hours, sleep_hours, phone_hours, stress_level, mood_val, sleep_quality=None):
    # This mirrors the logic in ml_pipeline.py for deterministic productivity scoring
    p_score = 50
    
    if 7 <= sleep_hours <= 9: 
        p_score += 15
        if sleep_quality and sleep_quality >= 4: p_score += 10
    else: 
        p_score -= 10
        if sleep_quality and sleep_quality <= 2: p_score -= 10
    
    if 2 < study_hours <= 8: p_score += 20
    elif study_hours > 8: p_score -= (study_hours - 8) * 5
    
    if phone_hours > 3: p_score -= (phone_hours - 3) * 5
    
    if mood_val == 2: p_score += 10
    elif mood_val == 0: p_score -= 10
    
    if stress_level >= 4: p_score -= 10
    
    return max(0, min(100, p_score))

def generate_personalized_plan(productivity_score, sleep_hours, sleep_quality, sleep_bedtime):
    plan = []
    
    # Analyze sleep
    if sleep_quality and sleep_quality < 3:
        plan.append("🌅 Morning: Gentle start. Your sleep quality was low. Avoid heavy caffeine first thing.")
    else:
        plan.append("🌅 Morning: Focus block. Direct your peak energy into your hardest subject.")
        
    if productivity_score > 70:
        plan.append("🏫 Afternoon: Deep work session. You're in a high productivity cycle.")
    else:
        plan.append("🏫 Afternoon: Review and light tasks. Focus on organization and small wins.")
        
    # Analyze sleep schedule
    bedtime_suggestion = "11:00 PM"
    if sleep_bedtime:
        try:
            # Simple heuristic for bedtime logic
            hour = int(sleep_bedtime.split(':')[0])
            if hour >= 23 or hour < 4:
                bedtime_suggestion = "10:30 PM (Try sleeping 30 mins earlier than last night)"
        except:
            pass
            
    plan.append(f"🌙 Evening: Digital detox at 9 PM. Target sleep at {bedtime_suggestion}.")
    
    return " | ".join(plan)

def get_suggestions(burnout_risk, productivity_score):
    suggestions = []
    
    if burnout_risk == "High":
        suggestions.append("🚨 HIGH BURNOUT RISK! Please take a full day off to rest.")
    elif burnout_risk == "Medium":
        suggestions.append("You're pushing it. Schedule regular 15-minute breaks.")
    
    if productivity_score < 40:
        suggestions.append("Try the Pomodoro technique to boost focus.")
    elif productivity_score > 80:
        suggestions.append("You are in the zone! Keep up the momentum.")
        
    if not suggestions:
        suggestions.append("Doing great! Maintain your balance.")
        
    return " | ".join(suggestions)

def predict_burnout(study_hours: float, sleep_hours: float, phone_hours: float, stress_level: int, mood_str: str, sleep_bedtime: str = None, sleep_quality: int = None):
    mood_val = map_mood_to_int(mood_str)
    
    if model is None:
        # Fallback to heuristic if model fails
        burnout_risk = "Medium" if stress_level >= 4 or study_hours > 10 else "Low"
    else:
        input_data = pd.DataFrame({
            'study_hours': [study_hours],
            'sleep_hours': [sleep_hours],
            'phone_usage_hours': [phone_hours],
            'stress_level': [stress_level],
            'mood': [mood_val]
        })
        burnout_risk = model.predict(input_data)[0]
    
    productivity_score = calculate_productivity_score(study_hours, sleep_hours, phone_hours, stress_level, mood_val, sleep_quality)
    suggestions = get_suggestions(burnout_risk, productivity_score)
    
    # Add personalized plan to suggestions
    personalized_plan = generate_personalized_plan(productivity_score, sleep_hours, sleep_quality, sleep_bedtime)
    final_suggestions = f"{suggestions} || PLAN: {personalized_plan}"
    
    return burnout_risk, productivity_score, final_suggestions
