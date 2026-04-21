import sqlite3
import os

def up():
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS t_car_info_history_pics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        history_id INTEGER,
        path TEXT,
        created_at TEXT
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Migration 7: car_history_pics table created successfully")

def down():
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS t_car_info_history_pics')
    conn.commit()
    conn.close()
    print("Migration 7: car_history_pics table dropped")

if __name__ == '__main__':
    up()