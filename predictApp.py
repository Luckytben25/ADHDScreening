from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
from datetime import datetime

app = Flask(__name__)

# Load model, scaler, and features
model = pickle.load(open("lr_model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))
features = pickle.load(open("features.pkl", "rb"))  # list of feature names

@app.route("/")
def home():
    return render_template("checklist.html")  # or your dashboard page

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()  # JSON from frontend (AJAX)
        user_features = data.get("features", {})

        # Validate all required features are present
        missing = [f for f in features if f not in user_features]
        if missing:
            return jsonify({"error": f"Missing features: {', '.join(missing)}"}), 400

        # Prepare input
        X = [user_features[f] for f in features]
        X = np.array([X], dtype=float)

        # Scale input
        X_scaled = scaler.transform(X)

        # Prediction and probability
        prediction = model.predict(X_scaled)[0]
        proba = model.predict_proba(X_scaled)[0][1]  # probability of ADHD

        # Determine risk level
        if proba >= 0.75:
            risk_level = "High"
            message = "Strong ADHD indicators. Please consult a professional."
        elif proba >= 0.40:
            risk_level = "Medium"
            message = "Moderate signs of ADHD. Further evaluation recommended."
        else:
            risk_level = "Low"
            message = "Unlikely ADHD, but consult a professional if concerned."

        # Response for API (AJAX)
        return jsonify({
            "prediction": int(prediction),
            "probability": round(float(proba), 4),
            "risk_level": risk_level,
            "message": message
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/result")
def result_page():
    # Example data (in real scenario, redirect after prediction or store in session)
    result = {
        "prediction": 1,
        "probability": 0.82,
        "risk_level": "High",
        "message": "Strong ADHD indicators. Please consult a professional.",
        "created_at": datetime.now()
    }
    return render_template("result.html", **result)

if __name__ == "__main__":
    app.run(debug=True)
