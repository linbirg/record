import sqlite3
import os

def up():
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('ALTER TABLE t_car_no_history ADD COLUMN user_name TEXT')
    
    conn.commit()
    conn.close()
    print("Migration 8: added user_name column to t_car_no_history")

def down():
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('ALTER TABLE t_car_no_history DROP COLUMN user_name')
    conn.commit()
    conn.close()
    print("Migration 8: dropped user_name column from t_car_no_history")

if __name__ == '__main__':
    up()