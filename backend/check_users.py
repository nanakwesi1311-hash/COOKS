# check_users.py
import sqlite3

conn = sqlite3.connect("C:/Users/KAY/Desktop/COOKS/backend/database.db")  # path must match your actual db
cursor = conn.cursor()

cursor.execute("SELECT username, password FROM users")
users = cursor.fetchall()

for user in users:
    print("Username:", user[0])
    print("Hashed Password:", user[1])

conn.close()
