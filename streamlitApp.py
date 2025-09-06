# streamlit_app.py
import streamlit as st
import os
import pickle
import joblib
import numpy as np
import pandas as pd
import importlib

st.set_page_config(page_title="ADHD Screening", layout="centered")

# --- Adjust filenames if your files have different names ---
MODEL_PATH = "lr_model.pkl"
SCALER_PATH = "scaler.pkl"
FEATURES_PATH = "features.pkl"
SAMPLE_CSV = "adhdTest.csv"   # optional sample CSV

# --- Helpers to load artifacts ---
def try_joblib_or_pickle(path):
    if not os.path.exists(path):
        return None
    # try joblib first
    try:
        return joblib.load(path)
    except Exception:
        pass
    # fallback to pickle
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None

@st.cache_data
def load_artifacts():
    model = try_joblib_or_pickle(MODEL_PATH)
    scaler = try_joblib_or_pickle(SCALER_PATH)
    features = try_joblib_or_pickle(FEATURES_PATH)
    sample_df = pd.read_csv(SAMPLE_CSV) if os.path.exists(SAMPLE_CSV) else None
    # if features not provided, infer from sample csv
    if features is None and sample_df is not None:
        features = list(sample_df.columns)
    # remove common label names if present
    if features is not None:
        labels = {"label","target","diagnosis","ADHD","Outcome","Result"}
        features = [f for f in features if f not in labels]
    return model, scaler, features, sample_df

model, scaler, features, sample_df = load_artifacts()

st.title("ADHD Screening — Demo")
st.write("The UI will try to build inputs from `features.pkl` or `adhdTest.csv`. If you have `predictApp.prepare_input()` implemented, the app will use it.")

if model is None:
    st.error(f"Model not found at `{MODEL_PATH}`. Put your model file in the same folder as this script.")
    st.stop()

# Try to import predictApp (optional)
predict_mod = None
try:
    predict_mod = importlib.import_module("predictApp")
except Exception:
    predict_mod = None

if features is None:
    st.warning("No `features.pkl` or sample CSV found. Edit streamlit_app.py to add the expected feature names.")
    st.stop()

# Build input form
with st.form("input_form"):
    st.info("Fill the inputs — they are created from features list.")
    user_inputs = {}
    # Use sample_df to infer numeric vs categorical when available
    for feat in features:
        if sample_df is not None and feat in sample_df.columns:
            ser = sample_df[feat].dropna()
            if pd.api.types.is_numeric_dtype(ser):
                vmin, vmax = float(ser.min()), float(ser.max())
                default = float(ser.median())
                step = max((vmax - vmin) / 100.0, 0.01)
                user_inputs[feat] = st.number_input(feat, min_value=vmin, max_value=vmax, value=default, step=step, format="%.4f")
            else:
                uniques = ser.unique().tolist()
                if 1 <= len(uniques) <= 30:
                    choice = st.selectbox(feat, options=uniques)
                    # store raw choice (we will attempt to encode later)
                    user_inputs[feat] = choice
                else:
                    user_inputs[feat] = st.text_input(feat, value=str(uniques[0]) if len(uniques)>0 else "")
        else:
            # fallback numeric input
            user_inputs[feat] = st.number_input(feat, value=0.0, step=0.1, format="%.4f")
    submitted = st.form_submit_button("Predict")

if submitted:
    # If predictApp provides prepare_input, use it (recommended)
    if predict_mod is not None and hasattr(predict_mod, "prepare_input"):
        try:
            X = predict_mod.prepare_input(user_inputs)  # user should implement this to return (1, n_features) np.array
            X = np.asarray(X, dtype=float)
        except Exception as e:
            st.error(f"predictApp.prepare_input failed: {e}")
            st.stop()
    else:
        # Fallback: simple numeric conversion in feature order
        try:
            row = []
            for feat in features:
                val = user_inputs[feat]
                # if val is string but looks numeric, convert
                if isinstance(val, str):
                    try:
                        val = float(val)
                    except Exception:
                        # if categorical string, try mapping from sample_df if present
                        if sample_df is not None and feat in sample_df.columns:
                            uniques = sample_df[feat].dropna().unique().tolist()
                            if val in uniques:
                                val = float(uniques.index(val))
                            else:
                                # unknown category -> 0
                                val = 0.0
                        else:
                            val = 0.0
                row.append(val)
            X = np.array([row], dtype=float)
        except Exception as e:
            st.error(f"Failed to build input array: {e}")
            st.stop()

    # Apply scaler if present and model likely expects scaled inputs
    if scaler is not None:
        try:
            X = scaler.transform(X)
        except Exception as e:
            st.warning(f"Scaler transform failed or incompatible: {e} — continuing without scaler.")

    # Run prediction
    try:
        pred = model.predict(X)
        st.success("Prediction complete")
        st.write("Predicted class / label:")
        st.write(pred[0])
        if hasattr(model, "predict_proba"):
            st.write("Probabilities:")
            st.write(model.predict_proba(X)[0])
    except Exception as e:
        st.error(f"Model prediction failed: {e}")
        st.stop()
