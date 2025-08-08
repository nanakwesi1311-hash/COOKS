import os
import sqlite3
import json
from passlib.context import CryptContext
from fastapi import HTTPException

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../users.db")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'doctor'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            created_by TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagnoses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            diagnosed_by TEXT NOT NULL,
            input_data TEXT,
            disease TEXT,
            prescription TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def register_admin():
    if not get_user_by_username("admin"):
        register_user("admin", "adminpass", "admin")


def register_user(username, password, role="doctor"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    hashed_pw = pwd_context.hash(password)
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_pw, role))
    conn.commit()
    conn.close()


def authenticate_user(username, password):
    user = get_user_by_username(username)
    if user and pwd_context.verify(password, user["password"]):
        return user
    return False


def get_user_by_username(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, role FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"username": row[0], "password": row[1], "role": row[2]}
    return None


def get_all_users_from_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "username": r[1], "role": r[2]} for r in rows]


def delete_user_from_db(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


def create_patient(name, age, gender, created_by):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO patients (name, age, gender, created_by) VALUES (?, ?, ?, ?)", (name, age, gender, created_by))
    conn.commit()
    conn.close()


def get_patients(created_by):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age, gender FROM patients WHERE created_by = ?", (created_by,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "age": r[2], "gender": r[3]} for r in rows]


def get_all_patients_from_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age, gender, created_by FROM patients")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "age": r[2], "gender": r[3], "created_by": r[4]} for r in rows]


def delete_patient_from_db(patient_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"}


def save_diagnosis(patient_id, diagnosed_by, input_data, disease, prescription):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO diagnoses (patient_id, diagnosed_by, input_data, disease, prescription) VALUES (?, ?, ?, ?, ?)",
                   (patient_id, diagnosed_by, json.dumps(input_data), disease, prescription))
    conn.commit()
    conn.close()


def get_diagnosis_history(patient_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT disease, prescription, input_data, timestamp FROM diagnoses WHERE patient_id = ? ORDER BY timestamp DESC", (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"disease": r[0], "prescription": r[1], "input_data": json.loads(r[2]), "timestamp": r[3]} for r in rows]


def get_all_diagnoses():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT patients.name, diagnoses.disease, diagnoses.prescription, diagnoses.timestamp FROM diagnoses JOIN patients ON diagnoses.patient_id = patients.id")
    rows = cursor.fetchall()
    conn.close()
    return [{"patient_name": r[0], "disease": r[1], "prescription": r[2], "timestamp": r[3]} for r in rows]
