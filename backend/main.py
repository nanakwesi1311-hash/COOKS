from fastapi import FastAPI, HTTPException, Depends
import os
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
from fastapi.responses import FileResponse
from utils.predictor import predict_disease_and_prescription
from utils.auth import authenticate_user, create_access_token, get_current_user
from utils.db_utils import (
    init_db,
    register_user,
    get_user_by_username,
    save_diagnosis,
    get_diagnosis_history,
    create_patient,
    get_patients,
    get_all_users_from_db,
    get_all_diagnoses,
    get_all_patients_from_db,
    delete_user_from_db,
    delete_patient_from_db,
    update_patient_in_db,
    register_admin,
    log_activity,
    get_activity_logs,
    get_system_updates,
    add_system_update,
    get_analytics_data,
    init_files_db,
    add_patient_file,
    get_patient_files,
    init_notifications_db,
    create_notification,
    get_notifications,
    mark_notifications_read
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
import shutil

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

init_db()
init_files_db()
init_notifications_db()
register_admin()

class TokenRequest(BaseModel):
    username: str
    password: str

class PredictionRequest(BaseModel):
    data: Dict[str, str]
    patient_id: int

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "doctor"

class PatientRequest(BaseModel):
    name: str
    age: int
    gender: str

@app.post("/register")
def register_user_endpoint(user: RegisterRequest):
    if get_user_by_username(user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    register_user(user.username, user.password, user.role)
    return {"message": "User registered successfully"}

@app.post("/token")
def login(request: TokenRequest):
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    log_activity(user["username"], "login")
    if user["role"] != "admin":
        create_notification(f"Doctor {user['username']} logged into the system", "login")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    log_activity(current_user["username"], "logout")
    return {"message": "Logged out successfully"}

@app.post("/predict")
def predict_endpoint(request: PredictionRequest, current_user: dict = Depends(get_current_user)):
    from utils.db_utils import get_patient_by_id
    patient = get_patient_by_id(request.patient_id)
    if patient:
        request.data["Age"] = str(patient["age"])
        request.data["Gender"] = patient["gender"]

    disease, prescription = predict_disease_and_prescription(request.data)
    # save_diagnosis is removed from here to allow "Save or Trash" on frontend
    return {"disease": disease, "prescription": prescription, "message": "Clinical decision support analysis complete."}

class SaveDiagnosisRequest(BaseModel):
    patient_id: int
    data: Dict[str, str]
    disease: str
    prescription: str

@app.post("/save-diagnosis")
def save_diagnosis_endpoint(request: SaveDiagnosisRequest, current_user: dict = Depends(get_current_user)):
    save_diagnosis(request.patient_id, current_user["username"], request.data, request.disease, request.prescription)
    create_notification(f"New decision support analysis saved by Dr. {current_user['username']}", "diagnosis")
    return {"message": "Decision support data saved successfully"}

@app.post("/patients")
def add_patient(patient: PatientRequest, current_user: dict = Depends(get_current_user)):
    create_patient(patient.name, patient.age, patient.gender, current_user["username"])
    return {"message": "Patient added successfully"}


@app.get("/patients")
def list_patients(current_user: dict = Depends(get_current_user)):
    return get_patients(current_user["username"])

@app.put("/patients/{patient_id}")
def update_patient(patient_id: int, patient: PatientRequest, current_user: dict = Depends(get_current_user)):
    # Check if the user is a doctor or admin (main.py assumes current_user is valid)
    success = update_patient_in_db(patient_id, patient.name, patient.age, patient.gender)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found or update failed")
    return {"message": "Patient updated successfully"}

from fastapi import UploadFile, File

@app.post("/patients/{patient_id}/upload")
async def upload_file(patient_id: int, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    file_path = os.path.join(UPLOAD_DIR, f"{patient_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    add_patient_file(patient_id, file.filename, f"/uploads/{patient_id}_{file.filename}")
    return {"message": "File uploaded successfully"}

@app.get("/patients/{patient_id}/files")
def list_files(patient_id: int, current_user: dict = Depends(get_current_user)):
    return get_patient_files(patient_id)

@app.get("/history/{patient_id}")
def get_history(patient_id: int, current_user: dict = Depends(get_current_user)):
    return get_diagnosis_history(patient_id)

@app.get("/admin/users")
def admin_users(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return get_all_users_from_db()

@app.get("/admin/patients")
def admin_patients(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return get_all_patients_from_db()

@app.get("/admin/logs")
def get_logs(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return get_activity_logs()

@app.get("/admin/system-updates")
def list_system_updates(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return get_system_updates()

class SystemUpdateRequest(BaseModel):
    title: str
    description: str

@app.post("/admin/system-updates")
def post_system_update(update: SystemUpdateRequest, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    add_system_update(update.title, update.description)
    return {"message": "Update posted successfully"}

@app.get("/admin/analytics")
def get_admin_analytics(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return get_analytics_data()

@app.delete("/admin/users/{username}")
def delete_user(username: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    if username == current_user["username"]:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")
    return delete_user_from_db(username)

@app.delete("/admin/patients/{patient_id}")
def delete_patient(patient_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return delete_patient_from_db(patient_id)

@app.get("/admin/notifications")
def list_notifications(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return get_notifications()

@app.post("/admin/notifications/read")
def read_notifications(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    mark_notifications_read()
    return {"message": "Notifications marked as read"}

@app.get("/")
def root():
    return {"message": "Clinical decision support system is running."}
