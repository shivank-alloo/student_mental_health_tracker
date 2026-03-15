import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import json

def generate_synthetic_data(num_samples=1000):
    np.random.seed(42)
    
    # Generate random data
    study_hours = np.random.uniform(0, 14, num_samples)
    sleep_hours = np.random.uniform(2, 12, num_samples)
    phone_usage_hours = np.random.uniform(0, 10, num_samples)
    stress_level = np.random.randint(1, 6, num_samples) # Stress from 1 to 5
    
    # Categorical mood (0: bad, 1: ok, 2: good) represented by numbers for easy mapping later
    moods = np.random.choice([0, 1, 2], num_samples, p=[0.2, 0.5, 0.3])
    
    # Calculate Burnout Risk Rules (synthetic logic)
    # High burnout if: high study (>8), low sleep (<6), bad mood (0)
    burnout_risk = []
    productivity_score = []
    
    for i in range(num_samples):
        b_score = 0
        p_score = 50 # base productivity
        
        # Burnout logic
        if study_hours[i] > 8: b_score += 2
        if sleep_hours[i] < 6: b_score += 3
        if phone_usage_hours[i] > 6: b_score += 1
        if moods[i] == 0: b_score += 2
        if stress_level[i] >= 4: b_score += 2
        
        if b_score >= 5:
            burnout_risk.append("High")
        elif b_score >= 3:
            burnout_risk.append("Medium")
        else:
            burnout_risk.append("Low")
            
        # Productivity Logic
        if sleep_hours[i] >= 7 and sleep_hours[i] <= 9: p_score += 20
        else: p_score -= 10
        
        if study_hours[i] > 2 and study_hours[i] <= 8: p_score += 20
        elif study_hours[i] > 8: p_score -= (study_hours[i] - 8) * 5
        
        if phone_usage_hours[i] > 3: p_score -= (phone_usage_hours[i] - 3) * 5
        
        if moods[i] == 2: p_score += 10
        elif moods[i] == 0: p_score -= 10
        
        # Clip productivity between 0 and 100
        p_score = max(0, min(100, p_score))
        productivity_score.append(p_score)
        
    df = pd.DataFrame({
        'study_hours': study_hours,
        'sleep_hours': sleep_hours,
        'phone_usage_hours': phone_usage_hours,
        'stress_level': stress_level,
        'mood': moods,
        'burnout_risk': burnout_risk,
        'productivity_score': productivity_score
    })
    
    return df

def train_model():
    print("Generating synthetic data...")
    df = generate_synthetic_data(2000)
    # Save the synthetic dataset for Person 2's task
    df.to_csv("student_data.csv", index=False)
    print("Dataset saved to student_data.csv")
    
    # Features and Targets
    X = df[['study_hours', 'sleep_hours', 'phone_usage_hours', 'stress_level', 'mood']]
    
    # Target 1: Burnout Risk (Classification)
    y_burnout = df['burnout_risk']
    
    # Target 2: Productivity Score (We'll treat it as a regression or bin it, 
    # but let's train a model for burnout first. For productivity we can use a simple regressor,
    # or just calculate it via a heuristic in the app since it's deterministic here.
    # Let's train a RandomForest for Burnout for demonstration of ML.)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_burnout, test_size=0.2, random_state=42)
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    print("Training Burnout Classifier...")
    clf.fit(X_train, y_train)
    
    print("Evaluating Model:")
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred))
    
    # Save the model
    model_path = "burnout_model.joblib"
    joblib.dump(clf, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_model()
