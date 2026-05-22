import os
from utils.db_utils import init_db

db_path = os.path.join("C:\Users\Nana Kwesi\Desktop\COOKS\backend\database.db")

# Delete the existing DB file
if os.path.exists(db_path):
    os.remove(db_path)
    print("✅ Deleted old database.")
else:
    print("ℹ️ No existing database found.")

# Recreate the tables
init_db()
print("✅ Created a new fresh database.")
