import sqlite3
import os
from passlib.context import CryptContext

# Setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")
conn.commit()

# --- Menu ---
print("\nUser Management Options:")
print("1. Add new user")
print("2. List all users")
print("3. Reset user database (delete all users)")
choice = input("Enter your choice (1/2/3): ")

# --- Add user ---
if choice == "1":
    username = input("Enter username: ")
    password = input("Enter password: ")
    hashed_password = pwd_context.hash(password)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        print("✅ User added successfully.")
    except sqlite3.IntegrityError:
        print(f"❌ Username '{username}' already exists.")

# --- List users ---
elif choice == "2":
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    if users:
        print("\nRegistered Users:")
        for user in users:
            print(f"• ID: {user[0]}, Username: {user[1]}")
    else:
        print("No users found.")

# --- Reset database ---
elif choice == "3":
    confirm = input("⚠️ Are you sure you want to delete all users? (yes/no): ")
    if confirm.lower() == "yes":
        cursor.execute("DELETE FROM users")
        conn.commit()
        print("✅ All users have been deleted.")
    else:
        print("Cancelled.")

else:
    print("❌ Invalid choice.")

# Close connection
conn.close()
