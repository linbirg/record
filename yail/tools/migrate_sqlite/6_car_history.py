import sqlite3
import os

def up():
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS t_car_info_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_id INTEGER,
        user_name TEXT,
        dept TEXT,
        carid TEXT,
        brand TEXT,
        car_license TEXT,
        license TEXT,
        abbr TEXT,
        deleted_at TEXT DEFAULT (datetime('now', 'localtime'))
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS t_car_no_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_id INTEGER,
        old_car_no TEXT,
        new_car_no TEXT,
        changed_at TEXT DEFAULT (datetime('now', 'localtime'))
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Migration 6: car_history tables created successfully")

def down():
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS t_car_info_history')
    cursor.execute('DROP TABLE IF EXISTS t_car_no_history')
    conn.commit()
    conn.close()
    print("Migration 6: car_history tables dropped")

if __name__ == '__main__':
    up()