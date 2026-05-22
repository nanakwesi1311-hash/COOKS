import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Migrating database at {DB_PATH}...")
    
    # Check if is_online column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "is_online" not in columns:
        print("Adding is_online column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN is_online INTEGER DEFAULT 0")
    
    if "last_seen" not in columns:
        print("Adding last_seen column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN last_seen TIMESTAMP")
        
    # Ensure logs and system_updates tables exist (init_db should do this but lets be safe)
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
    
    conn.commit()
    conn.close()
    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate()
