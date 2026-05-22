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
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            is_online INTEGER DEFAULT 0,
            last_seen TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    cursor.execute("SELECT id, username, role, is_online, last_seen FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "username": r[1], "role": r[2], "is_online": r[3], "last_seen": r[4]} for r in rows]


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


def update_patient_in_db(patient_id, name, age, gender):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE patients SET name = ?, age = ?, gender = ? WHERE id = ?", (name, age, gender, patient_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_patients(created_by):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age, gender FROM patients WHERE created_by = ?", (created_by,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "age": r[2], "gender": r[3]} for r in rows]

def get_patient_by_id(patient_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age, gender FROM patients WHERE id = ?", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "age": row[2], "gender": row[3]}
    return None


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
    cursor.execute("SELECT disease, prescription, input_data, timestamp, diagnosed_by FROM diagnoses WHERE patient_id = ? ORDER BY timestamp DESC", (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"disease": r[0], "prescription": r[1], "input_data": json.loads(r[2]), "timestamp": r[3], "diagnosed_by": r[4]} for r in rows]


def get_all_diagnoses():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT patients.name, diagnoses.disease, diagnoses.prescription, diagnoses.timestamp FROM diagnoses JOIN patients ON diagnoses.patient_id = patients.id")
    rows = cursor.fetchall()
    conn.close()
    return [{"patient_name": r[0], "disease": r[1], "prescription": r[2], "timestamp": r[3]} for r in rows]


def log_activity(username, action):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (username, action) VALUES (?, ?)", (username, action))
    is_online = 1 if action == "login" else 0
    cursor.execute("UPDATE users SET is_online = ?, last_seen = CURRENT_TIMESTAMP WHERE username = ?", (is_online, username))
    conn.commit()
    conn.close()

def get_activity_logs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, action, timestamp FROM logs ORDER BY timestamp DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return [{"username": r[0], "action": r[1], "timestamp": r[2]} for r in rows]

def get_system_updates():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, timestamp FROM system_updates ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"title": r[0], "description": r[1], "timestamp": r[2]} for r in rows]

def add_system_update(title, description):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO system_updates (title, description) VALUES (?, ?)", (title, description))
    conn.commit()
    conn.close()



def log_activity(username, action):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (username, action) VALUES (?, ?)", (username, action))
    is_online = 1 if action == "login" else 0
    cursor.execute("UPDATE users SET is_online = ?, last_seen = CURRENT_TIMESTAMP WHERE username = ?", (is_online, username))
    conn.commit()
    conn.close()

def get_activity_logs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, action, timestamp FROM logs ORDER BY timestamp DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return [{"username": r[0], "action": r[1], "timestamp": r[2]} for r in rows]

def get_system_updates():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, timestamp FROM system_updates ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"title": r[0], "description": r[1], "timestamp": r[2]} for r in rows]

def add_system_update(title, description):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO system_updates (title, description) VALUES (?, ?)", (title, description))
    conn.commit()
    conn.close()



def get_analytics_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Disease Distribution
    cursor.execute("SELECT disease, COUNT(*) FROM diagnoses GROUP BY disease ORDER BY COUNT(*) DESC")
    disease_counts = [{"name": r[0], "value": r[1]} for r in cursor.fetchall()]
    
    # 2. Diagnoses over time (last 30 days)
    cursor.execute("""
        SELECT date(timestamp) as day, COUNT(*) 
        FROM diagnoses 
        WHERE timestamp >= date("now", "-30 days")
        GROUP BY day 
        ORDER BY day ASC
    """)
    daily_stats = [{"date": r[0], "count": r[1]} for r in cursor.fetchall()]
    
    conn.close()
    return {"diseaseDistribution": disease_counts, "dailyStats": daily_stats}



def get_analytics_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Disease Distribution
    cursor.execute("SELECT disease, COUNT(*) FROM diagnoses GROUP BY disease ORDER BY COUNT(*) DESC")
    disease_counts = [{"name": r[0], "value": r[1]} for r in cursor.fetchall()]
    
    # 2. Diagnoses over time (last 30 days)
    cursor.execute("""
        SELECT date(timestamp) as day, COUNT(*) 
        FROM diagnoses 
        WHERE timestamp >= date("now", "-30 days")
        GROUP BY day 
        ORDER BY day ASC
    """)
    daily_stats = [{"date": r[0], "count": r[1]} for r in cursor.fetchall()]
    
    conn.close()
    return {"diseaseDistribution": disease_counts, "dailyStats": daily_stats}



def init_files_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            file_name TEXT,
            file_path TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_patient_file(patient_id, file_name, file_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO patient_files (patient_id, file_name, file_path) VALUES (?, ?, ?)", (patient_id, file_name, file_path))
    conn.commit()
    conn.close()

def get_patient_files(patient_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT file_name, file_path, timestamp FROM patient_files WHERE patient_id = ?", (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"name": r[0], "path": r[1], "timestamp": r[2]} for r in rows]



def init_files_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            file_name TEXT,
            file_path TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_patient_file(patient_id, file_name, file_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO patient_files (patient_id, file_name, file_path) VALUES (?, ?, ?)", (patient_id, file_name, file_path))
    conn.commit()
    conn.close()

def get_patient_files(patient_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT file_name, file_path, timestamp FROM patient_files WHERE patient_id = ?", (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"name": r[0], "path": r[1], "timestamp": r[2]} for r in rows]



def init_notifications_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            type TEXT,
            is_read INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def create_notification(message, type="info"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notifications (message, type) VALUES (?, ?)", (message, type))
    conn.commit()
    conn.close()

def get_notifications():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, message, type, is_read, timestamp FROM notifications ORDER BY timestamp DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "message": r[1], "type": r[2], "is_read": r[3], "timestamp": r[4]} for r in rows]

def mark_notifications_read():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET is_read = 1")
    conn.commit()
    conn.close()



def init_notifications_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            type TEXT,
            is_read INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def create_notification(message, type="info"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notifications (message, type) VALUES (?, ?)", (message, type))
    conn.commit()
    conn.close()

def get_notifications():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, message, type, is_read, timestamp FROM notifications ORDER BY timestamp DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "message": r[1], "type": r[2], "is_read": r[3], "timestamp": r[4]} for r in rows]

def mark_notifications_read():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET is_read = 1")
    conn.commit()
    conn.close()

