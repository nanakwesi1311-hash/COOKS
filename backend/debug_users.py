import sqlite3

conn = sqlite3.connect("C:/Users/KAY/Desktop/COOKS/backend/users.db")
cursor = conn.cursor()
cursor.execute("SELECT username FROM users")
users = cursor.fetchall()
print("Users:", users)
conn.close()
