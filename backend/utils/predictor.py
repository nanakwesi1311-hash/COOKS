import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Initialize the Gemini client
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

def predict_disease_and_prescription(symptoms_data):
    if not client:
        return "Configuration Error", "GEMINI_API_KEY is not set in the environment variables."

    # Format the patient profile into a prompt
    prompt = f"""
    You are an expert Chief Medical Officer and AI clinical decision support expert.
    Analyze the following patient profile and symptoms to provide the most likely medical diagnosis and standard clinical prescription/recommendation.

    Patient Profile:
    - Age: {symptoms_data.get('Age', 'Unknown')}
    - Gender: {symptoms_data.get('Gender', 'Unknown')}
    - Weight: {symptoms_data.get('Weight', 'Unknown')} kg
    - Height: {symptoms_data.get('Height', 'Unknown')} feet
    - Blood Pressure: {symptoms_data.get('Blood Pressure', 'Unknown')}
    - Heart Rate: {symptoms_data.get('Heart Rate', 'Unknown')} bpm
    - Cholesterol Level: {symptoms_data.get('Cholesterol Level', 'Unknown')}
    
    Medical History & Lifestyle:
    - Pre-existing Conditions: {symptoms_data.get('Pre-existing Conditions', 'None reported')}
    - Family Medical History: {symptoms_data.get('Family Medical History', 'None reported')}
    - Known Allergies: {symptoms_data.get('Known Allergies', 'None reported')}
    - Smoking Status: {symptoms_data.get('Smoking Status', 'Unknown')}
    - Alcohol Consumption: {symptoms_data.get('Alcohol Consumption', 'Unknown')}
    
    Symptoms:
    {symptoms_data.get('Symptoms', 'No specific symptoms provided.')}

    CRITICAL INSTRUCTION: First, evaluate if the input symptoms and profile are genuinely related to health, medicine, or a physical/mental condition. 
    If the user inputs gibberish, general conversation, or something completely unrelated to health (e.g., "how to bake a cake", "what is the capital of France", "asdfghjkl"):
    - Set "disease" to "Non-Medical Input"
    - Set "prescription" to "The input provided does not appear to be related to a medical condition or health issue. Please describe valid medical symptoms."

    Otherwise, return your response strictly as a JSON object with two keys:
    "disease": The most likely disease name (string)
    "prescription": A brief, standard clinical prescription or recommendation (string)
    
    Do not include any markdown formatting, explanation, or code blocks in the output. Just the JSON object.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        # Clean response string if Gemini adds markdown blocks
        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        
        result = json.loads(clean_text)
        return result.get("disease", "Unknown"), result.get("prescription", "Consult a physician")

    except Exception as e:
        import traceback
        error_msg = str(e)
        # Log error to file for diagnosis
        try:
            with open("c:\\Users\\Nana Kwesi\\Desktop\\COOKS\\backend\\error_log.txt", "w") as f:
                f.write(f"API Key (obfuscated): {api_key[:5]}...{api_key[-5:] if api_key else ''}\n")
                f.write(f"Error Message: {error_msg}\n")
                f.write(f"Traceback:\n{traceback.format_exc()}\n")
        except Exception as log_err:
            print(f"Failed to log error to file: {log_err}")
            
        print(f"Gemini API Error: {e}")
        if any(err in error_msg for err in ["503", "UNAVAILABLE", "high demand", "502", "Bad Gateway", "Quota exceeded", "Resource has been exhausted", "rate limit"]):
            return "Service Overloaded", "The AI diagnostic model is currently experiencing exceptionally high demand or a temporary network error. Please wait a few moments and click 'Run Prediction' again."
        return "Analysis Error", f"Could not process symptoms: {error_msg}. Please try again or consult a physician."

if __name__ == "__main__":
    test_input = {
        "Age": "45",
        "Gender": "Male",
        "Blood Pressure": "High",
        "Cholesterol Level": "Normal",
        "Symptoms": "Severe chest pain radiating to the left arm, shortness of breath, sweating."
    }
    print(predict_disease_and_prescription(test_input))
