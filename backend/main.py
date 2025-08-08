from fastapi import FastAPI, HTTPException, Depends
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
    register_admin
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
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
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/predict")
def predict_endpoint(request: PredictionRequest, current_user: dict = Depends(get_current_user)):
    disease, prescription = predict_disease_and_prescription(request.data)
    save_diagnosis(request.patient_id, current_user["username"], request.data, disease, prescription)
    return {"disease": disease, "prescription": prescription}

@app.post("/patients")
def add_patient(patient: PatientRequest, current_user: dict = Depends(get_current_user)):
    create_patient(patient.name, patient.age, patient.gender, current_user["username"])
    return {"message": "Patient added successfully"}


@app.get("/patients")
def list_patients(current_user: dict = Depends(get_current_user)):
    return get_patients(current_user["username"])

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

@app.get("/admin/diagnoses")
def admin_diagnoses(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return get_all_diagnoses()

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

@app.get("/")
def root():
    return {"message": "Disease diagnosis system is running."}
