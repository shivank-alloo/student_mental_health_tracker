import pandas as pd
import matplotlib.pyplot as plt
import seaborn as plt_sns
import os

# Set style
plt_sns.set_theme(style="whitegrid")
os.makedirs("static", exist_ok=True)

def generate_analytics():
    print("Generating Analytics...")
    try:
        df = pd.read_csv("student_data.csv")
    except FileNotFoundError:
        print("Error: student_data.csv not found. Please run ml_pipeline.py first.")
        return

    # Map mood to descriptive labels for visualization
    mood_labels = {0: "Bad", 1: "OK", 2: "Good"}
    df['mood_label'] = df['mood'].map(mood_labels)

    # 1. Mood vs Productivity Boxplot
    plt.figure(figsize=(8, 6))
    plt_sns.boxplot(x='mood_label', y='productivity_score', data=df, order=["Bad", "OK", "Good"], palette="Set2")
    plt.title("Impact of Daily Mood on Productivity Score")
    plt.xlabel("Daily Mood")
    plt.ylabel("Productivity Score (0-100)")
    plt.savefig("static/mood_vs_productivity.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved mood_vs_productivity.png")

    # 2. Study Hours vs Burnout Risk Scatterplot / Swarmplot
    plt.figure(figsize=(8, 6))
    # We will use a violin plot to show distribution of study hours across burnout risk categories
    plt_sns.violinplot(x='burnout_risk', y='study_hours', data=df, order=["Low", "Medium", "High"], palette="muted", inner="quartile")
    plt.title("Study Hours Distribution by Burnout Risk")
    plt.xlabel("Burnout Risk Level")
    plt.ylabel("Study Hours")
    plt.savefig("static/study_hours_burnout.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved study_hours_burnout.png")

    # 3. Correlation Heatmap
    plt.figure(figsize=(8, 6))
    corr = df[['study_hours', 'sleep_hours', 'phone_usage_hours', 'stress_level', 'productivity_score']].corr()
    plt_sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Correlation Between Lifestyle Factors and Productivity")
    plt.savefig("static/correlation_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved correlation_heatmap.png")

if __name__ == "__main__":
    generate_analytics()
