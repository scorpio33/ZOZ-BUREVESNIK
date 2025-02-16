import sqlite3
import os

def check_database():
    db_path = 'bot_database.db'
    
    # Create database if it doesn't exist
    if not os.path.exists(db_path):
        print(f"Creating new database: {db_path}")
        open(db_path, 'w').close()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check existing tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in cursor.fetchall()}
    
    required_tables = {'users', 'operations', 'teams', 'live_positions', 'search_sectors'}
    missing_tables = required_tables - existing_tables
    
    if missing_tables:
        print("Missing tables:", missing_tables)
    else:
        print("All required tables exist")
    
    conn.close()
    return len(missing_tables) == 0

if __name__ == "__main__":
    check_database()