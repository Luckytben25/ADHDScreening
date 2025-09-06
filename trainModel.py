import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os

# Dataset path (update if filename changes)
file_path = "/Users/sg/Documents/ICBT/Bsc.SE/2ns sem/FP/CPT_II_ConnersContinuousPerformanceTest (2).csv"

# Load dataset with correct delimiter
df = pd.read_csv(file_path, delimiter=";")

# Features we’ll use
features = [
    "General TScore Omissions", "Adhd TScore Omissions", "Raw Score Omissions",
    "General TScore Commissions", "Adhd TScore Commissions", "Raw Score Commissions",
    "General TScore HitRT", "Raw Score HitRT", "General TScore VarSE",
    "Adhd TScore DPrime", "Raw Score DPrime"
]
label = "Adhd Confidence Index"

# Drop missing values
df = df.dropna(subset=features + [label])

# Select features (X) and target (y)
X = df[features]
y = df[label]

# Encode target if it’s categorical (turns strings into numbers)
y = y.astype("category").cat.codes

# Train-test split (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train a Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
print("\n📊 Model Performance:\n")
print(classification_report(y_test, y_pred))

# Save model
output_model = os.path.join(os.path.dirname(file_path), "adhd_model.pkl")
joblib.dump(model, output_model)
print(f"\n✅ Model saved at: {output_model}")
