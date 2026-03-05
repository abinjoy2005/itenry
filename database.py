import sqlite3
import os

DB_PATH = 'travel.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create tables based on architecture
    c.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            preferences TEXT
        );

        CREATE TABLE IF NOT EXISTS trip_experiences (
            trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            destination TEXT,
            trip_date TEXT,
            companion_type TEXT,
            stay_name TEXT,
            stay_price REAL,
            stay_rating REAL,
            total_expense REAL,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS places_visited (
            place_id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER,
            place_order INTEGER,
            place_name TEXT,
            place_rating REAL,
            entry_fee REAL,
            distance_from_prev REAL,
            travel_method TEXT,
            travel_cost REAL,
            travel_rating REAL,
            FOREIGN KEY(trip_id) REFERENCES trip_experiences(trip_id)
        );
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
