# predictor.py

def predict_disease_and_prescription(symptoms):
    fever = symptoms.get("Fever")
    cough = symptoms.get("Cough")
    fatigue = symptoms.get("Fatigue")
    breathing = symptoms.get("Difficulty Breathing")
    age = int(symptoms.get("Age", 0))
    gender = symptoms.get("Gender")
    bp = symptoms.get("Blood Pressure")
    chol = symptoms.get("Cholesterol Level")

    # Rule-based conditions (dataset-derived)
    if fever == "Yes" and cough == "Yes" and fatigue == "Yes" and breathing == "Yes" and bp == "Normal" and chol == "Normal":
        return "Pneumonia", "Antibiotics and rest"

    elif fever == "Yes" and cough == "No" and fatigue == "No" and breathing == "No" and bp == "Normal" and chol == "Normal":
        return "Migraine", "Pain relievers and rest"
    
    elif fever == "Yes" and cough == "No" and fatigue == "No" and breathing == "No" and bp == "High" and chol == "High":
        return "Hypertension", "Antihypertensives and diet"
    
    elif fever == "No" and cough == "No" and fatigue == "Yes" and breathing == "No" and bp == "Normal" and chol == "Normal":
        return "Kidney Cancer", "Angiotensin-Converting Enzyme (ACE) inhibitors and Angiotensin II Receptor Blockers (ARBs)"

    elif fever == "No" and cough == "No" and fatigue == "Yes" and breathing == "No" and bp == "Low" and chol == "Normal":
        return "Anemia", "Iron-rich foods and supplements"

    elif fever == "No" and cough == "Yes" and fatigue == "Yes" and breathing == "Yes" and bp == "Normal" and chol == "High":
        return "Asthma", "Inhalers and avoid triggers"

    elif fever == "Yes" and cough == "Yes" and fatigue == "No" and breathing == "Yes" and bp == "Low" and chol == "Normal":
        return "Malaria", "Aertemisinin-based combination therapy (ACT) and antimalarial drugs"
    
    elif fever == "Yes" and cough == "Yes" and fatigue == "Yes" and breathing == "Yes" and bp == "Normal" and chol == "Normal":
        return "Pnuemonia", "Azithromycin Dose Pack, Amoxicillin and rest"
    
    elif fever == "Yes" and cough == "No" and fatigue == "Yes" and breathing == "Yes" and bp == "High" and chol == "High":
        return "Cholera", "Oral rehydration salts, ciprofloxacin and antibiotics"

    else:
        return "Unknown", "Please consult a physician for accurate diagnosis"


# Example test
if __name__ == "__main__":
    test_input = {
        "Fever": "Yes",
        "Cough": "Yes",
        "Fatigue": "Yes",
        "Difficulty Breathing": "Yes",
        "Age": "25",
        "Gender": "Female",
        "Blood Pressure": "Normal",
        "Cholesterol Level": "Normal"
    }
    print(predict_disease_and_prescription(test_input))
