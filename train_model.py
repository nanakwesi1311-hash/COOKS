# train_model.py

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import json
import os

# Load dataset
df = pd.read_csv("Disease_symptom_and_patient_profile_dataset.csv")

# Drop 'Outcome Variable' if present
df.drop(columns=['Outcome Variable'], inplace=True, errors='ignore')

# Encode categorical columns
label_encoders = {}
for column in df.columns:
    if df[column].dtype == 'object':
        le = LabelEncoder()
        df[column] = le.fit_transform(df[column])
        label_encoders[column] = le

# Separate features and target
X = df.drop(columns=['Disease'])
y = df['Disease']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
print("Model Evaluation Report:\n")
print(classification_report(y_test, y_pred))

# Save model and encoders
os.makedirs("backend/model", exist_ok=True)
joblib.dump(model, "backend/model/disease_predictor_model.pkl")
joblib.dump(label_encoders, "backend/model/label_encoders.pkl")

# Save prescriptions mapping
prescriptions = {
    "Malaria": "Artemether-Lumefantrine",
    "Diabetes": "Metformin",
    "Asthma": "Salbutamol",
    "Hypertension": "Amlodipine",
    "COVID-19": "Rest, fluids, monitor symptoms",
    "Flu": "Antiviral medication"
}
with open("backend/model/prescriptions.json", "w") as f:
    json.dump(prescriptions, f)

print("Model, encoders, and prescriptions saved successfully.")



