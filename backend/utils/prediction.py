import joblib
import json
import os
import pandas as pd

# Paths
model_path = os.path.join("C:/Users/KAY/Desktop/COOKS/backend/model/disease_predictor_model.pkl")
encoders_path = os.path.join("C:/Users/KAY/Desktop/COOKS/backend/model/label_encoders.pkl")
prescriptions_path = os.path.join("C:/Users/KAY/Desktop/COOKS/backend/model/prescriptions.json")

# Load model and encoders
model = joblib.load(model_path)
label_encoders = joblib.load(encoders_path)

# Load prescription mapping
with open(prescriptions_path, "r") as f:
    prescriptions = json.load(f)

def predict_disease(input_data: dict):
    input_df = {}

    # Encode features
    for feature, value in input_data.items():
        if feature in label_encoders:
            encoder = label_encoders[feature]
            try:
                input_df[feature] = encoder.transform([value])[0]
            except:
                raise ValueError(f"Invalid value '{value}' for feature '{feature}'")
        else:
            input_df[feature] = value

    input_df = pd.DataFrame([input_df])

    # Predict disease
    encoded_prediction = model.predict(input_df)[0]
    disease = label_encoders["Disease"].inverse_transform([encoded_prediction])[0]

    # Get prescription
    prescription = prescriptions.get(disease, "Consult a doctor.")
    return disease, prescription
