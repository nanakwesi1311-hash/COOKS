# backend/create_users_table.py

import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
""")

# Optional: Add a test user with hashed password
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash("test123")

cursor.execute("INSERT OR REPLACE INTO users (username, password) VALUES (?, ?)",
               ("john_doe", hashed_password))

conn.commit()
conn.close()

print("Users table created and test user added.")
