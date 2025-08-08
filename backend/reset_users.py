# reset_users.py
import sqlite3

conn = sqlite3.connect("backend/database.db")
cursor = conn.cursor()

# Drop the users table if it exists
cursor.execute("DROP TABLE IF EXISTS users")

# Recreate the users table
cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()
conn.close()

print("✅ Users table reset successfully.")
