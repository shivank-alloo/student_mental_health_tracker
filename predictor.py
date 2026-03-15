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
    from datetime import datetime
    current_hour = datetime.now().hour
    plan = []
    
    # Morning Logic (4 AM - 12 PM)
    if current_hour < 12:
        if sleep_quality and sleep_quality < 3:
            plan.append("🌅 Morning (Rest of Day): Gentle start recommended. Your sleep quality was low. Focus on organization.")
        else:
            plan.append("🌅 Morning (Rest of Day): Focus block! You're well-rested. Tackle your most complex study task now.")
    
    # Afternoon Logic (12 PM - 6 PM)
    if current_hour < 18:
        if productivity_score > 70:
            plan.append("🏫 Afternoon: Deep work session. You're in a high productivity cycle. Keep the momentum.")
        else:
            plan.append("🏫 Afternoon: Light review. Take a walk outside to reset your focus.")

    # Evening Logic (6 PM - End of Day)
    bedtime_suggestion = "11:00 PM"
    if sleep_bedtime:
        try:
            hour = int(sleep_bedtime.split(':')[0])
            if hour >= 23 or hour < 4:
                bedtime_suggestion = "10:30 PM (Earlier than last night for recovery)"
        except: pass
            
    plan.append(f"🌙 Evening: Digital detox at 9 PM. Aim for sleep at {bedtime_suggestion}.")
    
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
    
    # Combine everything
    final_suggestions = f"{suggestions} || PLAN: {personalized_plan}"
    
    return burnout_risk, productivity_score, final_suggestions

def study_user_trends(history_entries):
    """
    Analyzes historical entries to find behavioral patterns.
    """
    if not history_entries or len(history_entries) < 3:
        return "Need more data to study your behavior patterns."
        
    trends = []
    
    # Check for late sleep trend
    late_sleeps = [e for e in history_entries if e.sleep_bedtime and (int(e.sleep_bedtime.split(':')[0]) >= 23 or int(e.sleep_bedtime.split(':')[0]) < 4)]
    if len(late_sleeps) >= 2:
        avg_stress = sum(e.stress_level for e in late_sleeps) / len(late_sleeps)
        if avg_stress >= 3.5:
            trends.append("💡 Behavior Insight: Your stress level spikes significantly on days following late-night bedtimes.")

    # Check for high phone usage trend
    high_phone = [e for e in history_entries if e.phone_usage_hours > 5]
    if len(high_phone) >= 2:
        avg_prod = sum(e.productivity_score for e in high_phone) / len(high_phone)
        if avg_prod < 50:
            trends.append("💡 Behavior Insight: High screen time (>5h) consistently drops your productivity below 50%.")
            
    if not trends:
        return "You're maintaining a consistent balance. No negative behavior patterns detected lately."
        
    return " ".join(trends)
