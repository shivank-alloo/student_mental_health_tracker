# AI Student Mental Health & Productivity Tracker

## Overview
The **AI Student Mental Health & Productivity Tracker** is a minimal, AI-enhanced web application designed to help students track their daily habits (study hours, sleep, phone usage, stress, and mood) and understand how these factors influence burnout risk and productivity.

This repository represents the **Phase 1 Foundation & MVP** built by our 6-person team.

## Features
- **Daily Logging:** Log your mood, study hours, sleep hours, phone usage, and stress levels.
- **AI-Powered Insights:** Uses a Scikit-Learn RandomForestClassifier to predict `burnout_risk`.
- **Productivity Scoring:** Deterministic scoring system to track daily effectiveness.
- **Analytics Dashboard:** Beautiful frontend with interactive charts and dynamic ML-generated routines based on user data.
- **Data Insights:** Generates a synthetic dataset (`student_data.csv`) and visualizes key trends (e.g., impact of mood on productivity).

## Tech Stack
- **Backend:** FastAPI (Python), SQLAlchemy, SQLite
- **Machine Learning:** Scikit-Learn, Pandas, NumPy, Joblib
- **Frontend:** HTML, CSS, Vanilla JS
- **Visualization:** Matplotlib, Seaborn

## Setup & Installation

### Prerequisites
- Python 3.9+
- Pip

### 1. Backend & ML Setup
```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (ensure fastapi, uvicorn, sqlalchemy, scikit-learn, pandas, etc. are installed)
pip install fastapi uvicorn sqlalchemy pydantic scikit-learn pandas numpy joblib matplotlib seaborn

# Generate synthetic data & train the model
python ml_pipeline.py

# Generate Analytics visualizations
python analytics.py

# Run the FastAPI server
uvicorn main:app --reload
```

### 2. Frontend Setup
Simply open `static/index.html` in your web browser. Or, serve it via Python:
```bash
cd static
python -m http.server 8080
```
Then navigate to `http://localhost:8080/index.html` in your browser.

## Team Output & Roles
* **Person 1 (ML / Lead):** Project Idea Document (`project_idea.md`) & architecture.
* **Person 2 (Data Science):** Synthetic Dataset (`student_data.csv`).
* **Person 3 (Backend):** FastAPI routes (`main.py`, `models.py`, `schemas.py`).
* **Person 4 (Frontend):** UI implementation (`static/index.html`, `app.js`, `style.css`).
* **Person 5 (Analytics):** Visualizations (`analytics.py`, producing charts in the `static/` directory).
* **Person 6 (Documentation):** `README.md` and repository management.
